// Mechanism probe only. Never preloaded into the timed investigation.
#include <cstdio>
#include <dlfcn.h>
extern "C" void png_set_compression_level(void* png, int level) {
  using Setter = void (*)(void*, int);
  auto setter = reinterpret_cast<Setter>(dlsym(RTLD_NEXT, "png_set_compression_level"));
  std::fprintf(stderr, "PNG_LEVEL %d\n", level);
  setter(png, level);
}
