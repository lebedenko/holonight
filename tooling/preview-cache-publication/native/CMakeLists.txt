cmake_minimum_required(VERSION 3.25)
project(cache_publication_correctness LANGUAGES CXX)
find_package(HolonightFileBrowser REQUIRED CONFIG COMPONENTS Preview)
find_package(Qt6 REQUIRED COMPONENTS Test)
find_package(GTest 1.14 REQUIRED CONFIG)
add_executable(publication-correctness main.cpp
  ${FROZEN}/holonight-images/tests/isolated_verification_test.cpp
  ${FROZEN}/holonight-images/tests/isolated_generation_test.cpp
  ${FROZEN}/holonight-images/tests/isolated_cleanup_test.cpp)
target_compile_features(publication-correctness PRIVATE cxx_std_23)
target_compile_definitions(publication-correctness PRIVATE
  FROZEN_PREVIEW_TEST="${FROZEN}/holonight-file-browser/tests/isolated_preview_test.cpp"
  BROWSER_TEST_RUNTIME="${RUNTIME}" BROWSER_TEST_FIXTURES="${FIXTURES}")
target_link_libraries(publication-correctness PRIVATE HolonightFileBrowser::Preview Qt6::Test GTest::gtest)
target_sources(publication-correctness PRIVATE
  ${FROZEN}/holonight-file-browser/tests/session_pool_test.cpp)
add_executable(session-correctness ${FROZEN}/holonight-images/tests/isolated_session_test.cpp)
target_compile_features(session-correctness PRIVATE cxx_std_23)
target_link_libraries(session-correctness PRIVATE HolonightImages::Isolated Qt6::Test GTest::gtest)
add_executable(images-consumer ${FROZEN}/holonight-images/tests/package-consumer/main.cpp)
target_link_libraries(images-consumer PRIVATE HolonightImages::Images)
add_executable(preview-consumer preview-consumer.cpp)
target_link_libraries(preview-consumer PRIVATE HolonightFileBrowser::Preview Qt6::Test)
