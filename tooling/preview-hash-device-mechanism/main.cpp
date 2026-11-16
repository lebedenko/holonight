#include <QCoreApplication>
#include <QCryptographicHash>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QTemporaryDir>
#include <array>
#include <chrono>
#include <iostream>
#include <map>
#include <memory>
#include <stdexcept>

using Clock = std::chrono::steady_clock;
constexpr qsizetype Chunk = 65536;
const QStringList Cases = {"device_buffered",     "device_unbuffered",
                           "stream_1k_buffered",  "stream_1k_unbuffered",
                           "stream_64k_buffered", "stream_64k_unbuffered",
                           "memory_1k",           "memory_64k"};
class CountingFile : public QFile {
public:
  using QFile::QFile;
  std::map<std::pair<qint64, qint64>, qint64> histogram;

protected:
  qint64 readData(char *data, qint64 requested) override {
    auto returned = QFile::readData(data, requested);
    ++histogram[{requested, returned}];
    return returned;
  }
};
void check(bool ok, const char *message) {
  if (!ok)
    throw std::runtime_error(message);
}
qint64 elapsed(Clock::time_point start) {
  return std::chrono::duration_cast<std::chrono::nanoseconds>(Clock::now() -
                                                              start)
      .count();
}
QJsonObject readJson(const QString &path) {
  QFile f(path);
  check(f.open(QIODevice::ReadOnly), "JSON open failed");
  QJsonParseError error;
  auto doc = QJsonDocument::fromJson(f.readAll(), &error);
  check(error.error == QJsonParseError::NoError && doc.isObject(),
        "invalid JSON");
  return doc.object();
}
struct Result {
  QByteArray digest;
  qint64 init = 0, update = 0, final = 0, bytes = 0;
  qint64 reads = 0, updates = 0;
  QJsonArray histogram;
};
void validateRead(qint64 count, bool atEnd) {
  check(count >= 0, "file read failed");
  check(count != 0 || atEnd, "unexpected zero read");
}
Result hash(const QString &kind, const QString &path, const QByteArray &memory,
            bool counting) {
  const bool mem = kind.startsWith("memory"),
             device = kind.startsWith("device");
  const qint64 chunk = kind.contains("64k") ? 65536 : 1024;
  // Timed file arms use ordinary QFile, never the instrumented subclass.
  std::unique_ptr<QFile> file = counting ? std::make_unique<CountingFile>(path)
                                         : std::make_unique<QFile>(path);
  if (!mem) {
    QIODevice::OpenMode flags = QIODevice::ReadOnly;
    if (kind.endsWith("unbuffered"))
      flags |= QIODevice::Unbuffered;
    check(file->open(flags), "file open failed");
  }
  std::array<char, Chunk> buffer{};
  Result r;
  auto start = Clock::now();
  auto qt = std::make_unique<QCryptographicHash>(QCryptographicHash::Sha256);
  r.init = elapsed(start);
  start = Clock::now();
  if (device) {
    check(qt->addData(file.get()), "Qt device hash failed");
  } else {
    qint64 offset = 0;
    for (;;) {
      const char *data;
      qint64 count;
      if (mem) {
        count = std::min<qint64>(chunk, memory.size() - offset);
        data = memory.constData() + offset;
      } else {
        count = file->read(buffer.data(), chunk);
        if (counting)
          ++r.reads;
        data = buffer.data();
        validateRead(count, count == 0 && file->atEnd());
      }
      if (!count)
        break;
      qt->addData(QByteArrayView(data, count));
      if (counting)
        ++r.updates;
      offset += count;
    }
    r.bytes = offset;
  }
  r.update = elapsed(start);
  start = Clock::now();
  r.digest = qt->result();
  r.final = elapsed(start);
  // Common validation and instrumented output are outside all three timers.
  if (!mem) {
    check(file->error() == QFileDevice::NoError && file->atEnd() &&
              file->pos() == memory.size(),
          "file EOF/position/error mismatch");
    if (device)
      r.bytes = file->pos();
    check(r.bytes == file->pos(), "byte count/position mismatch");
    if (counting) {
      for (const auto &[sizes, calls] :
           static_cast<CountingFile *>(file.get())->histogram)
        r.histogram.append(QJsonObject{{"requested", sizes.first},
                                       {"returned", sizes.second},
                                       {"calls", calls}});
    }
  }
  return r;
}
void emitJson(const QJsonObject &row) {
  std::cout << QJsonDocument(row).toJson(QJsonDocument::Compact).constData()
            << std::endl;
}
void selfTest() {
  QTemporaryDir dir;
  check(dir.isValid(), "temporary directory failed");
  const QList<QByteArray> vectors = {
      QByteArray(),
      QByteArray("abc"),
      QByteArray("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq"),
      QByteArray(1023, 'x'),
      QByteArray(1024, 'y'),
      QByteArray(1025, 'z'),
      QByteArray(65535, 'a'),
      QByteArray(65536, 'b'),
      QByteArray(65537, 'c'),
      QByteArray(131079, 'd')};
  const QList<QByteArray> known = {
      "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
      "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"};
  int i = 0;
  for (const auto &data : vectors) {
    QString path = dir.path() + '/' + QString::number(i);
    QFile f(path);
    check(f.open(QIODevice::WriteOnly) && f.write(data) == data.size(),
          "fixture write failed");
    f.close();
    auto expected =
        QCryptographicHash::hash(data, QCryptographicHash::Sha256).toHex();
    if (i < known.size())
      check(expected == known[i], "standard vector mismatch");
    for (const auto &kind : Cases) {
      for (bool counting : {false, true}) {
        auto r = hash(kind, path, data, counting);
        check(r.digest.toHex() == expected && r.bytes == data.size(),
              "correctness mismatch");
      }
    }
    ++i;
  }
  for (const auto &kind : Cases) {
    for (const auto &path : {dir.path() + "/absent", dir.path()}) {
      bool failed = false;
      try {
        if (kind.startsWith("memory"))
          continue;
        hash(kind, path, {}, true);
      } catch (const std::exception &) {
        failed = true;
      }
      check(failed, "read failure accepted");
    }
  }
  for (auto failure : {qint64(-1), qint64(0)}) {
    bool failed = false;
    try {
      validateRead(failure, false);
    } catch (const std::exception &) {
      failed = true;
    }
    check(failed, "invalid read accepted");
  }
}
int main(int argc, char **argv) {
  QCoreApplication app(argc, argv);
  try {
    if (app.arguments().size() == 2 && app.arguments()[1] == "--self-test") {
      selfTest();
      return 0;
    }
    check(argc == 2 || (argc == 3 && app.arguments()[2] == "--count"),
          "expected registration path and optional --count");
    const bool counting = argc == 3;
    const auto reg = readJson(app.arguments()[1]);
    auto files = reg["mapping"].toArray();
    QList<QByteArray> memory;
    qint64 retained = 0;
    for (const auto &value : files) {
      auto row = value.toObject();
      QFile f(reg["runtime"].toString() + '/' + row["path"].toString());
      check(f.open(QIODevice::ReadOnly), "preload open failed");
      auto size = row["size"].toInteger();
      check(size >= 0 && retained + size <= 128 * 1024 * 1024 &&
                f.size() == size,
            "preload cap/size mismatch");
      auto bytes = f.readAll();
      check(f.error() == QFileDevice::NoError && bytes.size() == size,
            "preload read failed");
      check(
          QCryptographicHash::hash(bytes, QCryptographicHash::Sha256).toHex() ==
              row["sha256"].toString().toLatin1(),
          "preload digest mismatch");
      retained += size;
      memory.append(bytes);
    }
    QFile maps("/proc/self/maps");
    check(maps.open(QIODevice::ReadOnly), "maps unavailable");
    emitJson({{"type", "identity"},
              {"pid", QCoreApplication::applicationPid()},
              {"counting", counting},
              {"maps", QString::fromUtf8(maps.readAll())}});
    for (const auto &value :
         reg[counting ? "count_schedule" : "schedule"].toArray()) {
      auto sweep = value.toObject();
      auto kind = sweep["case"].toString();
      check(Cases.contains(kind), "unknown case");
      auto sweepStart = Clock::now();
      for (int ordinal = 0; ordinal < files.size(); ++ordinal) {
        auto file = files[ordinal].toObject();
        auto r = hash(kind,
                      reg["runtime"].toString() + '/' + file["path"].toString(),
                      memory[ordinal], counting);
        check(r.bytes == file["size"].toInteger() &&
                  r.digest.toHex() == file["sha256"].toString().toLatin1(),
              "measured digest/size mismatch");
        check(elapsed(sweepStart) <= 30000000000LL, "sweep timeout");
        QJsonObject row = sweep;
        row.insert("type", "file");
        row.insert("ordinal", ordinal);
        row.insert("bytes", r.bytes);
        row.insert("sha256", QString::fromLatin1(r.digest.toHex()));
        row.insert("init_ns", r.init);
        row.insert("update_ns", r.update);
        row.insert("final_ns", r.final);
        if (counting) {
          row.insert("read_calls", kind.startsWith("device")
                                       ? QJsonValue()
                                       : QJsonValue(r.reads));
          row.insert("update_calls", kind.startsWith("device")
                                         ? QJsonValue()
                                         : QJsonValue(r.updates));
          row.insert("histogram", r.histogram);
        }
        emitJson(row);
      }
      emitJson({{"type", "sweep_end"},
                {"index", sweep["index"]},
                {"elapsed_ns", elapsed(sweepStart)}});
    }
    return 0;
  } catch (const std::exception &error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
