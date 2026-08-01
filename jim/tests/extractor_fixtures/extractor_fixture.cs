// A fixture for the path extractor. See test_the_extractors_agree.py.
public static class ExtractorFixture
{
    public static void Probe()
    {
        Post("/fixture/plain");
        Delete($"/fixture/{id}/nested");
    }
}
