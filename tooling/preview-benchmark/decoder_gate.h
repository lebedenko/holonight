// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <atomic>

// Private experiment admission gate. In-flight decoders still finish bounded cleanup.
class DecoderGate {
 public:
  bool admit() const { return !failed_.load(); }
  void complete(bool cleanupFailure) {
    if (cleanupFailure) failed_ = true;
  }
  bool failed() const { return failed_.load(); }

 private:
  std::atomic_bool failed_{false};
};
