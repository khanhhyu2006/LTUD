from pathlib import Path
courses=[
('Tiếng Anh Tiểu Học Khởi Đầu (Lớp 1–2)','Beginner',12,2400000,'Dành cho học sinh lớp 1–2; làm quen tiếng Anh qua tranh ảnh, trò chơi, bài hát và hội thoại ngắn. Nội dung gồm bảng chữ cái, số đếm, màu sắc, gia đình và trường học.','Nhận biết chữ cái và từ vựng quen thuộc; nghe hiểu chỉ dẫn đơn giản, tự giới thiệu và trả lời câu hỏi ngắn.'),
('Tiếng Anh Tiểu Học Phát Triển (Lớp 3–5)','Beginner',12,2800000,'Dành cho học sinh lớp 3–5; củng cố từ vựng và mẫu câu theo chủ đề, luyện nghe nói, đọc đoạn ngắn và viết câu cơ bản.','Giao tiếp các chủ đề sinh hoạt và học tập; đọc hiểu đoạn văn ngắn và viết đoạn giới thiệu bản thân có hướng dẫn.'),
('Tiếng Anh THCS Căn Bản (Lớp 6–7)','Beginner',12,3000000,'Dành cho học sinh lớp 6–7; hệ thống kiến thức ngữ pháp, phát âm và từ vựng phù hợp lứa tuổi, kết hợp luyện bốn kỹ năng và bài tập củng cố.','Vận dụng các thì và cấu trúc cơ bản; đọc hiểu thông tin chính, giao tiếp tình huống quen thuộc và viết đoạn văn ngắn.'),
('Tiếng Anh THCS Nâng Cao (Lớp 8–9)','Intermediate',14,3600000,'Dành cho học sinh lớp 8–9 đã có kiến thức căn bản; ôn tập ngữ pháp, từ vựng, đọc hiểu và viết, kết hợp luyện dạng bài kiểm tra và chuẩn bị thi vào lớp 10.','Củng cố kiến thức bậc THCS; cải thiện kỹ năng đọc hiểu, viết lại câu, viết đoạn và xử lý các dạng bài ôn thi vào lớp 10.'),
('Tiếng Anh THPT Phát Triển Kỹ Năng (Lớp 10–11)','Intermediate',12,3800000,'Dành cho học sinh lớp 10–11; mở rộng từ vựng, ngữ pháp và kỹ năng sử dụng tiếng Anh trong học tập, thuyết trình và thảo luận theo chủ đề.','Đọc hiểu văn bản ở mức phù hợp, trình bày ý kiến có lý do và viết đoạn văn mạch lạc theo chủ đề học tập.'),
('Ôn Thi Tiếng Anh Tốt Nghiệp THPT (Lớp 12)','Intermediate',16,4500000,'Dành cho học sinh lớp 12; hệ thống kiến thức tiếng Anh THPT, luyện đọc hiểu, từ vựng và ngữ pháp; thực hành đề tham khảo phù hợp với kỳ thi học viên đăng ký.','Xác định kiến thức còn yếu, xây dựng kế hoạch ôn tập và cải thiện độ chính xác, tốc độ xử lý các dạng bài luyện thi.'),
('Phonics Và Phát Âm Cho Trẻ Em','Beginner',8,1800000,'Dành cho trẻ bắt đầu học tiếng Anh; luyện nhận diện âm, ghép âm, trọng âm từ cơ bản và phát âm qua hoạt động nghe, đọc và trò chơi.','Nhận diện các âm thông dụng, ghép và đọc từ ngắn, hình thành thói quen nghe và phát âm rõ ràng.'),
('Cambridge Young Learners Starters–Movers','Beginner',14,3200000,'Dành cho học sinh tiểu học; làm quen hoạt động và dạng bài Cambridge Young Learners ở mức Starters hoặc Movers, lựa chọn nhóm học sau đánh giá đầu vào.','Mở rộng từ vựng và kỹ năng nghe, nói, đọc, viết; làm quen quy trình bài thi mẫu theo mức học phù hợp, không cam kết chứng chỉ.'),
('Củng Cố Tiếng Anh Căn Bản Cho Học Sinh','Beginner',10,2500000,'Dành cho học sinh THCS và THPT cần ôn lại kiến thức nền; học theo nhóm phù hợp độ tuổi, củng cố phát âm, từ loại, cấu trúc câu và các thì thường gặp.','Khắc phục các lỗ hổng kiến thức căn bản, sử dụng câu đơn rõ nghĩa và hình thành phương pháp tự học từ vựng, ngữ pháp.'),
('IELTS Foundation Cho Học Sinh THPT','Intermediate',12,4200000,'Dành cho học sinh THPT đã có tiếng Anh căn bản; xây dựng từ vựng học thuật, ngữ pháp, kỹ năng nghe và đọc, làm quen Speaking và Writing theo định dạng IELTS.','Hiểu cấu trúc bài thi IELTS, rèn các kỹ năng nền và xác định lộ trình luyện thi tiếp theo dựa trên đánh giá cuối khóa.')]
def q(v):return "N'"+v.replace("'","''")+"'"
values=',\n'.join('    ('+', '.join([q(n),q(l),str(w),str(f),q(d),q(o)])+')' for n,l,w,f,d,o in courses)
sql='''-- Học phí và thời lượng mẫu; không tạo lớp, lịch học hay phân công giáo viên.
SET NOCOUNT ON;
SET XACT_ABORT ON;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN TRANSACTION;
DECLARE @Courses TABLE (ProgramName nvarchar(150), Level nvarchar(50), DurationWeeks int, TuitionFee decimal(18,2), Description nvarchar(max), LearningOutcomes nvarchar(max));
INSERT INTO @Courses VALUES
'''+values+''';
INSERT INTO dbo.Programs (ProgramName,Level,DurationWeeks,TuitionFee,Description,LearningOutcomes,ImageUrl,IsActive,IsDeleted,DeletedAt,CreatedAt)
SELECT c.ProgramName,c.Level,c.DurationWeeks,c.TuitionFee,c.Description,c.LearningOutcomes,NULL,1,0,NULL,GETDATE()
FROM @Courses c
WHERE NOT EXISTS (SELECT 1 FROM dbo.Programs p WITH (UPDLOCK,HOLDLOCK) WHERE p.ProgramName=c.ProgramName);
SELECT @@ROWCOUNT AS InsertedCourses;
SELECT p.ProgramId,p.ProgramName,p.DurationWeeks,p.TuitionFee,p.IsActive,p.IsDeleted
FROM dbo.Programs p INNER JOIN @Courses c ON p.ProgramName=c.ProgramName ORDER BY p.ProgramId;
COMMIT TRANSACTION;
'''
out=Path('docs/database/add-school-courses.sql');out.parent.mkdir(exist_ok=True);out.write_text(sql,encoding='utf-8-sig')
print('Prepared',len(courses),'courses')
