using Microsoft.AspNetCore.Mvc;

namespace WedEnglishApp.Controllers
{
    public class PaymentController : Controller
    {
        public IActionResult Index()
        {
            return View();
        }
    }
}
