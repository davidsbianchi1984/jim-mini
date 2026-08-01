// A fixture for the path extractor. Its answer is written down in
// test_the_extractors_agree.py, so a capability lost here fails there rather
// than reporting a clean sweep.
func probe() async {
    _ = try? await request("/fixture/plain", method: "GET")
    _ = try? await request("/fixture/\(id)/nested", method: "DELETE")
}
