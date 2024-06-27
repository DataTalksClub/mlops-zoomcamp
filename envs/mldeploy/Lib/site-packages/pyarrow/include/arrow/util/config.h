// Licensed to the Apache Software Foundation (ASF) under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  The ASF licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing,
// software distributed under the License is distributed on an
// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied.  See the License for the
// specific language governing permissions and limitations
// under the License.

#define ARROW_VERSION_MAJOR 15
#define ARROW_VERSION_MINOR 0
#define ARROW_VERSION_PATCH 2
#define ARROW_VERSION ((ARROW_VERSION_MAJOR * 1000) + ARROW_VERSION_MINOR) * 1000 + ARROW_VERSION_PATCH

#define ARROW_VERSION_STRING "15.0.2"

#define ARROW_SO_VERSION "1500"
#define ARROW_FULL_SO_VERSION "1500.2.0"

#define ARROW_CXX_COMPILER_ID "MSVC"
#define ARROW_CXX_COMPILER_VERSION "19.16.27045.0"
#define ARROW_CXX_COMPILER_FLAGS "/DWIN32 /D_WINDOWS /GR /EHsc /D_SILENCE_TR1_NAMESPACE_DEPRECATION_WARNING"

#define ARROW_BUILD_TYPE "RELEASE"

#define ARROW_GIT_ID "e03105efc38edca4ca429bf967a17b4d0fbebe40"
#define ARROW_GIT_DESCRIPTION ""

#define ARROW_PACKAGE_KIND "python-wheel-windows"

#define ARROW_COMPUTE
#define ARROW_CSV
/* #undef ARROW_CUDA */
#define ARROW_DATASET
#define ARROW_FILESYSTEM
#define ARROW_FLIGHT
/* #undef ARROW_FLIGHT_SQL */
#define ARROW_IPC
/* #undef ARROW_JEMALLOC */
/* #undef ARROW_JEMALLOC_VENDORED */
#define ARROW_JSON
/* #undef ARROW_ORC */
#define ARROW_PARQUET
#define ARROW_SUBSTRAIT

#define ARROW_ENABLE_THREADING
#define ARROW_GCS
#define ARROW_S3
/* #undef ARROW_USE_NATIVE_INT128 */
/* #undef ARROW_WITH_MUSL */
/* #undef ARROW_WITH_OPENTELEMETRY */
/* #undef ARROW_WITH_UCX */
#define PARQUET_REQUIRE_ENCRYPTION
