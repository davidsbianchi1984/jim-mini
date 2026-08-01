// A fixture for the path extractor. See test_the_extractors_agree.py.
fun probe() {
    request("/fixture/plain", "GET")
    request("/fixture/$id/nested", "DELETE")
    val conn = (URL("$base/fixture/direct").openConnection() as HttpURLConnection).apply {
        requestMethod = "POST"
    }
}
