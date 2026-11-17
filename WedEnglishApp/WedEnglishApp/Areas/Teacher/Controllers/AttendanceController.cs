using Microsoft.AspNetCore.Mvc;

namespace WedEnglishApp.Areas.Teacher.Controllers
{
    public class AttendanceController : Controller
    {
        public IActionResult Index()
        {
            return View();
        }
    }
}
