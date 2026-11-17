// SPDX-License-Identifier: GPL-3.0-or-later
#include <QBuffer>
#include <QCryptographicHash>
#include <QFile>
#include <QTemporaryFile>
#include <QIODevice>
#include <algorithm>
#include <cstring>
#include <iostream>
#include <stdexcept>

#include "hash-loop.inc"

void check(bool value) {
  if (!value) throw std::runtime_error("streaming hash regression");
}
class ShortDevice : public QIODevice {
 public:
  QByteArray bytes;
  qint64 offset = 0;
  int failure;
  explicit ShortDevice(QByteArray data, int mode = 0) : bytes(std::move(data)), failure(mode) {
    open(QIODevice::ReadOnly | QIODevice::Unbuffered);
  }
  bool isSequential() const override { return true; }
  bool atEnd() const override { return offset == bytes.size() && failure == 0; }
  qint64 readData(char* target, qint64 maximum) override {
    if (offset >= 19 && failure) return failure == 1 ? -1 : 0;
    const auto size = std::min({maximum, qint64(7), bytes.size() - offset});
    std::memcpy(target, bytes.constData() + offset, size);
    offset += size;
    return size;
  }
  qint64 writeData(const char*, qint64) override { return -1; }
};
int main() {
  char buffer[65536];
  int cases = 0;
  for (const int size : {0, 1, 65535, 65536, 65537, 131072, 131073}) {
    QByteArray bytes(size, '\0');
    for (int i = 0; i < size; ++i) bytes[i] = char(i % 251);
    const auto expected = QCryptographicHash::hash(bytes, QCryptographicHash::Sha256);
    QTemporaryFile file;
    check(file.open()); check(file.write(bytes) == size); check(file.seek(0));
    QCryptographicHash control(QCryptographicHash::Sha256);
    check(control.addData(&file)); check(control.result() == expected); check(file.seek(0));
    QCryptographicHash candidate(QCryptographicHash::Sha256);
    check(streamRuntimeHash(file, candidate, size, buffer)); check(candidate.result() == expected);
    ShortDevice shortReads(bytes);
    QCryptographicHash shortHash(QCryptographicHash::Sha256);
    check(streamRuntimeHash(shortReads, shortHash, size, buffer)); check(shortHash.result() == expected);
    check(candidate.result() != QByteArray(32, '\xff')); // digest mismatch remains rejected
    ++cases;
  }
  for (const auto expectedSize : {31, 33}) {
    ShortDevice device(QByteArray(32, 'a'));
    QCryptographicHash hash(QCryptographicHash::Sha256);
    check(!streamRuntimeHash(device, hash, expectedSize, buffer)); ++cases;
  }
  for (int mode : {1, 2}) {
    ShortDevice device(QByteArray(64, 'a'), mode);
    QCryptographicHash hash(QCryptographicHash::Sha256);
    check(!streamRuntimeHash(device, hash, 64, buffer)); ++cases;
  }
  std::cout << "Passed " << cases << " streaming cases: empty, boundaries, short reads, truncation, extra bytes, errors, zero reads, digests\n";
}
