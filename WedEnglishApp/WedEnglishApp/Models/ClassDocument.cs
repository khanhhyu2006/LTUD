using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace WedEnglishApp.Models
{
    [Table("ClassDocuments")]
    public class ClassDocument
    {
        [Key]
        public int DocumentId { get; set; }

        [Required]
        public int ClassId { get; set; }

        [Required(ErrorMessage = "Tiêu đề tài liệu không được để trống")]
        [StringLength(200)]
        public string Title { get; set; } = string.Empty;

        [Required]
        [StringLength(255)]
        public string FilePath { get; set; } = string.Empty;

        public DateTime UploadedAt { get; set; } = DateTime.Now;
        public bool IsPublished { get; set; } = true;
        public DateTime? UpdatedAt { get; set; }

        // Navigation property
        [ForeignKey("ClassId")]
        public virtual CourseClass Class { get; set; } = null!;
    }
}
