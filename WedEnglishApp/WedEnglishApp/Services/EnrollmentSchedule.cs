namespace WedEnglishApp.Services;

public static class EnrollmentSchedule
{
    public static string? GetDays(string? pattern) => pattern switch
    {
        "246" => "2,4,6",
        "357" => "3,5,7",
        _ => null
    };
}
