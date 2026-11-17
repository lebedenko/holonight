// Private trial only. Included verbatim in the candidate and its native tests.
auto streamRuntimeHash = [](QIODevice& device, QCryptographicHash& hash, qint64 expectedBytes,
                            char* buffer) {
  qint64 bytes = 0;
  while (true) {
    const qint64 count = device.read(buffer, 65536);
    if (count < 0 || (count == 0 && !device.atEnd())) {
      return false;
    }
    if (count == 0) {
      return bytes == expectedBytes;
    }
    if (count > expectedBytes - bytes) {
      return false;
    }
    hash.addData(QByteArrayView(buffer, count));
    bytes += count;
  }
};
