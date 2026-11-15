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
#include <memory>
#include <openssl/evp.h>
#include <openssl/provider.h>
#include <stdexcept>

using Clock = std::chrono::steady_clock;
constexpr qsizetype Chunk = 65536;
const QStringList Cases = {"qt_device", "qt_file", "evp_file", "qt_memory",
                           "evp_memory"};
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
  qint64 init, update, final, bytes;
};
Result hash(const QString &kind, const QString &path, const QByteArray &memory,
            const EVP_MD *algorithm) {
  const bool evp = kind.startsWith("evp"), mem = kind.endsWith("memory");
  QFile file(path);
  if (!mem)
    check(file.open(QIODevice::ReadOnly), "file open failed");
  std::array<char, Chunk> buffer{};
  Result r{};
  auto start = Clock::now();
  std::unique_ptr<QCryptographicHash> qt;
  std::unique_ptr<EVP_MD_CTX, decltype(&EVP_MD_CTX_free)> ctx(nullptr,
                                                              EVP_MD_CTX_free);
  if (evp) {
    ctx.reset(EVP_MD_CTX_new());
    check(bool(ctx), "EVP allocation failed");
    check(EVP_DigestInit_ex(ctx.get(), algorithm, nullptr) == 1,
          "EVP init failed");
    check(EVP_MD_get0_provider(EVP_MD_CTX_get0_md(ctx.get())) ==
              EVP_MD_get0_provider(algorithm),
          "EVP context provider mismatch");
  } else
    qt = std::make_unique<QCryptographicHash>(QCryptographicHash::Sha256);
  r.init = elapsed(start);
  start = Clock::now();
  if (kind == "qt_device") {
    check(qt->addData(&file), "Qt device hash failed");
    check(file.error() == QFileDevice::NoError && file.atEnd(),
          "device read failed");
    r.bytes = file.pos();
  } else {
    qint64 offset = 0;
    for (;;) {
      const char *data;
      qint64 count;
      if (mem) {
        count = std::min<qint64>(Chunk, memory.size() - offset);
        data = memory.constData() + offset;
      } else {
        count = file.read(buffer.data(), Chunk);
        data = buffer.data();
        check(count >= 0, "file read failed");
        check(count != 0 || file.atEnd(), "unexpected zero read");
      }
      if (!count)
        break;
      if (evp)
        check(EVP_DigestUpdate(ctx.get(), data, size_t(count)) == 1,
              "EVP update failed");
      else
        qt->addData(QByteArrayView(data, count));
      offset += count;
    }
    r.bytes = offset;
  }
  r.update = elapsed(start);
  start = Clock::now();
  if (evp) {
    unsigned char digest[EVP_MAX_MD_SIZE];
    unsigned int size = 0;
    check(EVP_DigestFinal_ex(ctx.get(), digest, &size) == 1 && size == 32,
          "EVP final failed");
    r.digest = QByteArray(reinterpret_cast<char *>(digest), size);
  } else
    r.digest = qt->result();
  r.final = elapsed(start);
  return r;
}
void emitJson(const QJsonObject &row) {
  std::cout << QJsonDocument(row).toJson(QJsonDocument::Compact).constData()
            << std::endl;
}
void selfTest(const EVP_MD *algorithm) {
  QTemporaryDir dir;
  check(dir.isValid(), "temporary directory failed");
  const QList<QByteArray> vectors = {
      QByteArray(),
      QByteArray("abc"),
      QByteArray("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq"),
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
      auto r = hash(kind, path, data, algorithm);
      check(r.digest.toHex() == expected && r.bytes == data.size(),
            "correctness mismatch");
    }
    ++i;
  }
  for (const auto &kind :
       {QString("qt_device"), QString("qt_file"), QString("evp_file")}) {
    for (const auto &path : {dir.path() + "/absent", dir.path()}) {
      bool failed = false;
      try {
        hash(kind, path, {}, algorithm);
      } catch (const std::exception &) {
        failed = true;
      }
      check(failed, "read failure accepted");
    }
  }
}
int main(int argc, char **argv) {
  QCoreApplication app(argc, argv);
  try {
    // Fetch once outside all per-file timers and use this implementation for
    // every EVP context, so the recorded provider identifies the measured arm.
    std::unique_ptr<EVP_MD, decltype(&EVP_MD_free)> md(
        EVP_MD_fetch(nullptr, "SHA256", nullptr), EVP_MD_free);
    check(bool(md), "EVP provider unavailable");
    const auto *provider = EVP_MD_get0_provider(md.get());
    check(provider != nullptr, "missing EVP provider");
    if (app.arguments().size() == 2 && app.arguments()[1] == "--self-test") {
      selfTest(md.get());
      check(OSSL_PROVIDER_get0_name(provider) != nullptr,
            "provider name unavailable");
      return 0;
    }
    check(argc == 2, "expected registration path");
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
              {"provider", OSSL_PROVIDER_get0_name(provider)},
              {"maps", QString::fromUtf8(maps.readAll())}});
    for (const auto &value : reg["schedule"].toArray()) {
      auto sweep = value.toObject();
      auto kind = sweep["case"].toString();
      check(Cases.contains(kind), "unknown case");
      auto sweepStart = Clock::now();
      for (int ordinal = 0; ordinal < files.size(); ++ordinal) {
        auto file = files[ordinal].toObject();
        auto r = hash(kind,
                      reg["runtime"].toString() + '/' + file["path"].toString(),
                      memory[ordinal], md.get());
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
