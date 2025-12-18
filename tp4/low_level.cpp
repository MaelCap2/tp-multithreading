#include <chrono>
#include <iostream>
#include <string>

#include <Eigen/Dense>
#include <cpr/cpr.h>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

static Eigen::MatrixXd json_to_matrix(const json &A) {
  const int n = static_cast<int>(A.size());
  const int m = static_cast<int>(A.at(0).size());
  Eigen::MatrixXd M(n, m);
  for (int i = 0; i < n; ++i) {
    const auto &row = A.at(i);
    for (int j = 0; j < m; ++j) {
      M(i, j) = row.at(j).get<double>();
    }
  }
  return M;
}

static Eigen::VectorXd json_to_vector(const json &b) {
  const int n = static_cast<int>(b.size());
  Eigen::VectorXd v(n);
  for (int i = 0; i < n; ++i)
    v(i) = b.at(i).get<double>();
  return v;
}

static json vector_to_json(const Eigen::VectorXd &x) {
  json out = json::array();
  for (int i = 0; i < x.size(); ++i)
    out.push_back(x(i));
  return out;
}

static void usage(const char *prog) {
  std::cerr << "Usage: " << prog << " [--url http://127.0.0.1:8000] [--n 5]\n"
            << "  --url : base URL of the proxy\n"
            << "  --n   : number of tasks to process (default 5)\n";
}

int main(int argc, char **argv) {
  std::string base_url = "http://127.0.0.1:8000";
  int n_tasks = 5;

  for (int i = 1; i < argc; ++i) {
    const std::string arg = argv[i];
    if (arg == "--url" && i + 1 < argc) {
      base_url = argv[++i];
    } else if (arg == "--n" && i + 1 < argc) {
      n_tasks = std::stoi(argv[++i]);
    } else if (arg == "-h" || arg == "--help") {
      usage(argv[0]);
      return 0;
    } else {
      std::cerr << "Unknown argument: " << arg << "\n";
      usage(argv[0]);
      return 2;
    }
  }

  for (int k = 0; k < n_tasks; ++k) {
    // 1) GET a task (JSON)
    auto r = cpr::Get(cpr::Url{base_url + "/"});
    if (r.error) {
      std::cerr << "[C++] GET error: " << r.error.message << "\n";
      return 1;
    }
    if (r.status_code != 200) {
      std::cerr << "[C++] GET failed, status=" << r.status_code << "\n"
                << r.text << "\n";
      return 1;
    }

    json t;
    try {
      t = json::parse(r.text);
    } catch (const std::exception &e) {
      std::cerr << "[C++] JSON parse failed: " << e.what() << "\n";
      std::cerr << "Body was:\n" << r.text << "\n";
      return 1;
    }

    if (!t.contains("a") || !t.contains("b") || !t.contains("identifier") ||
        !t.contains("size")) {
      std::cerr << "[C++] Unexpected JSON schema. Got:\n" << t.dump(2) << "\n";
      return 1;
    }

    const int identifier = t["identifier"].get<int>();
    const int size = t["size"].get<int>();
    std::cout << "[C++] Task received: id=" << identifier << " size=" << size
              << "\n";

    Eigen::MatrixXd A = json_to_matrix(t["a"]);
    Eigen::VectorXd b = json_to_vector(t["b"]);

    auto start = std::chrono::high_resolution_clock::now();
    Eigen::VectorXd x = A.partialPivLu().solve(b);
    auto end = std::chrono::high_resolution_clock::now();
    const double seconds = std::chrono::duration<double>(end - start).count();

    t["x"] = vector_to_json(x);
    t["time"] = seconds;

    auto p = cpr::Post(cpr::Url{base_url + "/"},
                       cpr::Header{{"Content-Type", "application/json"}},
                       cpr::Body{t.dump()});

    if (p.error) {
      std::cerr << "[C++] POST error: " << p.error.message << "\n";
      return 1;
    }
    if (p.status_code != 200) {
      std::cerr << "[C++] POST failed, status=" << p.status_code << "\n"
                << p.text << "\n";
      return 1;
    }

    std::cout << "[C++] Result sent: id=" << identifier << " time=" << seconds
              << "s\n";
  }

  return 0;
}
