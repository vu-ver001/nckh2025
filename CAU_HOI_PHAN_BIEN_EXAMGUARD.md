# BỘ CÂU HỎI PHẢN BIỆN VÀ GỢI Ý TRẢ LỜI — EXAMGUARD

## Công thức trả lời ngắn gọn

Với phần lớn câu hỏi, trả lời theo bốn bước:

1. **Trả lời thẳng:** Có, không, hoặc hiện mới đạt đến mức nào.
2. **Nêu bằng chứng:** Dẫn một số liệu hoặc kết quả cụ thể.
3. **Nêu giới hạn:** Chỉ rõ điều gì chưa được kiểm chứng.
4. **Hướng tiếp theo:** Nói cách nhóm sẽ khắc phục.

Không nên cố bảo vệ hệ thống bằng mọi giá. Hội đồng thường đánh giá cao việc phân biệt rõ giữa kết quả đã chứng minh và mục tiêu tương lai.

---

# I. Câu hỏi có khả năng cao từ hội đồng cấp trường

## 1. Đề tài của nhóm giải quyết vấn đề gì?

**Gợi ý trả lời:**

“Đề tài giải quyết bài toán hỗ trợ giám thị tìm nhanh những thời điểm cần chú ý trong video thi. Hệ thống phát hiện điện thoại, tài liệu và một số tín hiệu tư thế, sau đó gửi cảnh báo kèm ảnh để giám thị xem lại. Hệ thống không thay thế giám thị và không tự kết luận một thí sinh gian lận.”

## 2. Điểm mới hoặc đóng góp chính của đề tài là gì?

**Gợi ý trả lời:**

“Nhóm không khẳng định đã sáng tạo một thuật toán AI hoàn toàn mới. Đóng góp chính là xây dựng được một nguyên mẫu tích hợp hoàn chỉnh: nhận video, phát hiện vật thể bằng YOLO, phân tích tư thế bằng MediaPipe, kết hợp bằng chứng theo thời gian, tạo cảnh báo, lưu ảnh và hiển thị trên dashboard. Điểm đáng chú ý là hệ thống không cảnh báo chỉ từ một khung hình mà yêu cầu bằng chứng tồn tại liên tục.”

## 3. Tại sao đề tài có ý nghĩa nếu quyết định cuối cùng vẫn thuộc về giám thị?

**Gợi ý trả lời:**

“Vai trò của hệ thống là sàng lọc, không phải thay thế con người. Với video dài hoặc nhiều vị trí cần quan sát, hệ thống có thể đánh dấu những thời điểm đáng chú ý để giám thị kiểm tra trước. Cách tiếp cận có con người trong vòng quyết định cũng phù hợp hơn về đạo đức, vì một tư thế bất thường chưa chắc là gian lận.”

## 4. Hệ thống định nghĩa thế nào là gian lận?

**Gợi ý trả lời:**

“Hệ thống không định nghĩa một hành vi là gian lận theo nghĩa kỷ luật. Hệ thống chỉ tạo các loại dấu hiệu cần rà soát như có điện thoại, có sách hoặc tài liệu, quay đầu, cúi đầu lâu hay đưa tay gần tai. Ý nghĩa cuối cùng còn phụ thuộc quy chế môn thi và quan sát của giám thị.”

## 5. Hệ thống đã được thử nghiệm trong phòng thi thật chưa?

**Gợi ý trả lời:**

“Chưa. Phạm vi hiện tại là sáu video pilot, một người và một camera. Các video giúp kiểm tra toàn bộ luồng kỹ thuật nhưng chưa đại diện cho một phòng thi thật có nhiều người, nhiều mức che khuất và nhiều góc camera. Đây là hạn chế lớn nhất và cũng là bước thực nghiệm tiếp theo.”

## 6. Độ chính xác của hệ thống là bao nhiêu?

**Gợi ý trả lời:**

“Nhóm không dùng một con số accuracy chung vì đây là bài toán phát hiện vật thể. Trên 214 ảnh validation, model điện thoại hiện tại đạt precision 61,39%, recall 47,33% và F1 53,45%. Điều đó cho thấy model đã cải thiện so với bản trước, nhưng recall 47,33% cũng có nghĩa là còn bỏ sót đáng kể. Nhóm chưa có đủ dữ liệu để công bố độ chính xác của toàn hệ thống trong phòng thi.”

## 7. Vì sao phát hiện 4/4 tình huống điện thoại mà không được nói chính xác 100%?

**Gợi ý trả lời:**

“Bốn trên bốn chỉ là số episode trong hai video dương tính của một bộ pilot rất nhỏ và nhãn còn sơ bộ. Đồng thời, hệ thống tạo sáu cảnh báo điện thoại ngoài các khoảng đã đánh dấu. Vì vậy, 4/4 chỉ cho thấy hệ thống không bỏ lỡ bốn episode này, không đủ để suy ra accuracy 100% hoặc khả năng tổng quát trong phòng thi.”

## 8. Nếu hệ thống còn cảnh báo nhầm thì có giá trị sử dụng không?

**Gợi ý trả lời:**

“Ở trạng thái hiện tại, hệ thống có giá trị như một nguyên mẫu nghiên cứu, chưa sẵn sàng triển khai thực tế. Sáu cảnh báo ngoài khoảng nhãn cho thấy cần giảm false positive trước khi sử dụng. Hướng khắc phục là bổ sung dữ liệu âm tính khó như máy tính và hộp bút, hiệu chỉnh ngưỡng và đánh giá theo số cảnh báo nhầm trên mỗi giờ video.”

## 9. Tại sao không để AI tự kết luận để giảm hoàn toàn công việc của giám thị?

**Gợi ý trả lời:**

“Vì tín hiệu hình ảnh không phản ánh đầy đủ bối cảnh. Cúi đầu có thể là viết bài, quay đầu có thể là phản xạ, và điện thoại có thể xuất hiện trong tình huống được phép trước hoặc sau giờ thi. Tự động kết luận có nguy cơ gây bất công. Do đó nhóm chủ động thiết kế hệ thống theo hướng hỗ trợ quyết định.”

## 10. Quyền riêng tư của thí sinh được xử lý như thế nào?

**Gợi ý trả lời:**

“Nguyên mẫu hiện chưa được triển khai thực tế nên chưa có quy trình vận hành hoàn chỉnh. Nếu triển khai, nhóm đề xuất thông báo rõ việc ghi hình, chỉ thu dữ liệu cần thiết, giới hạn người được truy cập, mã hóa khi lưu và truyền, quy định thời hạn lưu, ghi nhật ký truy cập và xóa dữ liệu đúng hạn. Cảnh báo phải được con người kiểm tra trước mọi quyết định.”

## 11. Đối tượng sử dụng hệ thống là ai?

**Gợi ý trả lời:**

“Đối tượng sử dụng là giám thị hoặc cán bộ phụ trách giám sát. Dashboard được thiết kế để hiển thị video, loại cảnh báo, thời điểm, điểm rủi ro và ảnh sự kiện. Hệ thống không hướng tới việc để thí sinh tự sử dụng hay để máy tự xử lý vi phạm.”

## 12. Nếu được làm tiếp, nhóm ưu tiên việc gì đầu tiên?

**Gợi ý trả lời:**

“Ưu tiên đầu tiên là xây dựng tập dữ liệu phòng thi độc lập và có nhãn được ít nhất hai người rà soát. Sau đó nhóm mới hiệu chỉnh ngưỡng, đo false alarms trên mỗi giờ, đo độ trễ và đánh giá theo từng góc camera. Khi chất lượng một camera ổn định, nhóm mới mở rộng sang nhiều người và nhiều camera.”

---

# II. Câu hỏi về thuật toán và thiết kế hệ thống

## 13. Tại sao chọn YOLO?

**Gợi ý trả lời:**

“YOLO là mô hình phát hiện vật thể một giai đoạn, có khả năng trả về cả loại vật thể và vị trí trong ảnh với tốc độ phù hợp cho video. Hệ sinh thái Ultralytics cũng thuận lợi cho huấn luyện, đánh giá và tích hợp. Tuy nhiên, nhóm chọn YOLO vì phù hợp bài toán nguyên mẫu, không khẳng định đây luôn là model tốt nhất nếu chưa có phép so sánh công bằng với các kiến trúc khác.”

## 14. Tại sao dùng cả YOLO-World và YOLOv8n chuyên điện thoại?

**Gợi ý trả lời:**

“YOLO-World dùng để quan sát nhiều loại vật thể bằng mô tả ngôn ngữ, còn YOLOv8n chuyên biệt cung cấp bounding box điện thoại. Thiết kế này cho phép vừa mở rộng danh sách vật thể, vừa có một nhánh chuyên cho điện thoại. Tuy nhiên, đối chứng hiện tại chưa chứng minh YOLO-World làm nhánh điện thoại tốt hơn checkpoint chuyên biệt, nên đây cũng là cơ sở để nhóm cân nhắc đơn giản hóa pipeline.”

## 15. MediaPipe thực hiện nhiệm vụ gì? Có nhận diện ánh mắt không?

**Gợi ý trả lời:**

“MediaPipe cung cấp các điểm hình học trên cơ thể và bàn tay. Nhóm sử dụng các điểm ở mũi, mắt, tai, vai, cổ tay và hông để tạo tín hiệu tư thế. Pipeline hiện tại không dùng Face Mesh và không nhận diện chính xác hướng nhìn của mắt. Vì vậy nhóm chỉ gọi sự kiện là quay đầu hoặc tư thế cần chú ý, không khẳng định người đó đang nhìn bài bên cạnh.”

## 16. Tại sao điện thoại phải xuất hiện ba lần và ít nhất 0,2 giây?

**Gợi ý trả lời:**

“Mục đích là loại bớt các dự đoán chập chờn chỉ xuất hiện ở một khung hình. Ba quan sát và 0,2 giây là cấu hình ban đầu phục vụ nguyên mẫu. Đây vẫn là ngưỡng heuristic, chưa được tối ưu trên dữ liệu phòng thi; muốn chốt ngưỡng cần đo quan hệ giữa tỷ lệ phát hiện, cảnh báo nhầm và độ trễ.”

## 17. Điểm rủi ro có phải xác suất gian lận không?

**Gợi ý trả lời:**

“Không. Điểm rủi ro là điểm theo quy tắc để sắp xếp mức chú ý. Ví dụ điện thoại có trọng số cao hơn quay đầu. Điểm chưa được hiệu chuẩn thành xác suất và không nên diễn giải rằng 18 điểm tương đương một tỷ lệ gian lận nào đó.”

## 18. Hệ thống phân biệt điện thoại với máy tính Casio hoặc hộp bút như thế nào?

**Gợi ý trả lời:**

“Hệ thống có danh sách vật thể được phép như máy tính khoa học và hộp bút, đồng thời dùng checkpoint chuyên điện thoại và kiểm tra tính liên tục theo thời gian. Tuy vậy, video pilot vẫn xuất hiện cảnh báo nhầm ở các cảnh vật dụng. Điều này cho thấy bộ lọc hiện tại chưa đủ và cần thêm hard negatives cũng như đánh giá lại ngưỡng.”

## 19. Nếu vật thể bị che hoặc quá nhỏ thì sao?

**Gợi ý trả lời:**

“Khả năng phát hiện giảm rõ rệt. Với điện thoại chiếm dưới 0,25% diện tích ảnh, recall hiện chỉ đạt 24,18%. Hướng cải thiện là bố trí camera gần hơn, dùng độ phân giải đầu vào phù hợp, bổ sung dữ liệu vật thể nhỏ và bị che, đồng thời thử các kỹ thuật chuyên cho small-object detection.”

## 20. Hệ thống có theo dõi được nhiều thí sinh không?

**Gợi ý trả lời:**

“Chưa. MediaPipe hiện xử lý một người và hệ thống chưa có ID tracking để gắn cảnh báo với từng thí sinh. Để mở rộng, cần thêm detector người, thuật toán multi-object tracking và cơ chế liên kết vật thể hoặc tư thế với đúng ID qua thời gian.”

## 21. Hệ thống có chạy thời gian thực không?

**Gợi ý trả lời:**

“Trên máy CPU Ryzen 5 PRO 6650U, pipeline xử lý khoảng 9,65 đến 10,95 FPS. Mức này đủ để trình diễn gần thời gian thực nhưng thấp hơn video nguồn 30 FPS và chưa bao gồm phép đo độ trễ end-to-end trên trình duyệt. Do đó nhóm chưa tuyên bố đáp ứng thời gian thực ở quy mô phòng thi.”

## 22. Nếu model hoặc camera gặp lỗi thì hệ thống phản ứng thế nào?

**Gợi ý trả lời:**

“Backend trả trạng thái lỗi nếu không mở được camera, video hoặc model. Cấu hình hiện tại không âm thầm thay MediaPipe bằng backend khác rồi tiếp tục báo sai tên model. Khi nguồn dừng, tài nguyên được đóng và FPS trở về 0. Trong triển khai thực tế vẫn cần bổ sung cảnh báo sức khỏe thiết bị và quy trình giám sát thủ công khi hệ thống lỗi.”

## 23. Tại sao không dùng Face Mesh hoặc nhận diện khuôn mặt?

**Gợi ý trả lời:**

“Nhóm giới hạn phạm vi để ưu tiên phát hiện điện thoại và tín hiệu tư thế cơ bản. Face Mesh chưa được tích hợp và nhận diện khuôn mặt cũng làm tăng vấn đề quyền riêng tư. Nếu nghiên cứu hướng nhìn trong tương lai, nhóm cần dữ liệu gán nhãn, phép đánh giá riêng và đánh giá tác động đạo đức trước khi bổ sung.”

## 24. Phần mềm sử dụng công nghệ gì?

**Gợi ý trả lời:**

“Phần xử lý chính viết bằng Python, sử dụng Ultralytics YOLO, PyTorch, MediaPipe và OpenCV. Backend dùng FastAPI; frontend dùng React và Vite. Video được truyền bằng MJPEG, cảnh báo gửi qua WebSocket, còn sự kiện được lưu dưới dạng CSV và ảnh snapshot.”

---

# III. Câu hỏi sâu về dữ liệu và kết quả

## 25. Dữ liệu có nguồn gốc từ đâu và được gán nhãn như thế nào?

**Gợi ý trả lời:**

“Tập điện thoại hiện dùng được mô tả là CITW, có nguồn từ COCO 2017. Dữ liệu gồm 1.600 ảnh train với 2.177 bounding box và 214 ảnh validation với 262 bounding box. Nhãn dùng định dạng YOLO, tức mỗi điện thoại được đánh dấu bằng một khung chữ nhật và mã lớp. Bộ audit hiện không phát hiện lỗi cấu trúc hoặc tệp trùng byte giữa hai phần dữ liệu.”

## 26. Tập validation có thực sự độc lập không?

**Gợi ý trả lời:**

“Không hoàn toàn. Tập 214 ảnh cũng được dùng trong quá trình chọn checkpoint nên có nguy cơ thiên lệch lựa chọn. Vì vậy nhóm gọi đây là validation, không gọi là test độc lập. Kết quả cuối cùng cần được đo lại trên tập mới, tách theo người, phòng và phiên quay.”

## 27. Precision và recall có ý nghĩa gì trong đề tài này?

**Gợi ý trả lời:**

“Precision trả lời câu hỏi: trong các bounding box mà model báo là điện thoại, bao nhiêu box khớp với nhãn thật. Recall trả lời: trong các điện thoại đã được gán nhãn, model tìm thấy được bao nhiêu. Precision 61,39% cho thấy vẫn còn báo nhầm; recall 47,33% cho thấy còn bỏ sót nhiều. Vì vậy phải xem đồng thời cả hai chỉ số.”

## 28. Vì sao có hai bộ số liệu: precision 59,457% và 61,39%?

**Gợi ý trả lời:**

“Hai số đến từ hai cách đánh giá khác nhau. Con số 59,457% nằm trong kết quả validation do Ultralytics lưu tại checkpoint tốt nhất trong quá trình train. Con số 61,39% đến từ script so sánh lại hai checkpoint trên cùng 214 ảnh, với confidence 0,30, NMS IoU 0,45 và IoU ghép nhãn 0,50. Khi trình bày so sánh checkpoint, nhóm dùng bộ 61,39% vì điều kiện đã được cố định và áp dụng giống nhau cho cả hai model.”

## 29. mAP của model là bao nhiêu và khác F1 thế nào?

**Gợi ý trả lời:**

“Checkpoint tốt nhất lưu mAP@0.5 là 50,806% và mAP@0.5:0.95 là 30,615%. mAP tổng hợp hiệu năng trên nhiều mức confidence, và mAP@0.5:0.95 còn xét nhiều ngưỡng độ chồng khung. F1 53,45% là kết quả tại một ngưỡng confidence cụ thể, kết hợp precision và recall. Vì cách tính khác nhau nên không so trực tiếp hai con số.”

## 30. Tại sao không so sánh với các nghiên cứu khác để chứng minh tốt hơn?

**Gợi ý trả lời:**

“Các nghiên cứu có thể dùng dữ liệu, định nghĩa hành vi, góc camera, phần cứng và chỉ số khác nhau. So sánh trực tiếp các phần trăm như vậy có thể gây hiểu nhầm. Nhóm chỉ nên kết luận hơn kém khi chạy các phương pháp trên cùng dữ liệu và cùng quy trình đánh giá; hiện nhóm chưa thực hiện phép so sánh đó.”

## 31. Sáu video có đủ để đánh giá không?

**Gợi ý trả lời:**

“Không. Sáu video chỉ đủ làm pilot để kiểm tra pipeline và phát hiện vấn đề ban đầu. Bộ này chưa đủ đa dạng về người, phòng, ánh sáng, vị trí camera hay mức che khuất. Nhóm cần nhiều phiên độc lập và nhãn được rà soát trước khi tính các chỉ số có ý nghĩa thống kê.”

## 32. Ai gán nhãn video và nhãn có đáng tin cậy không?

**Gợi ý trả lời:**

“Các khoảng điện thoại hiện được đánh dấu bằng rà khung hình mỗi 0,25 giây, nhưng trạng thái vẫn là nhãn sơ bộ và chưa có xác nhận của hai người đánh giá độc lập. Vì vậy nhóm ghi rõ hạn chế này và chưa dùng nhãn để tuyên bố kết quả nghiệm thu chính thức.”

## 33. 63/63 kiểm thử đạt có nghĩa model nhận diện tốt không?

**Gợi ý trả lời:**

“Không. Kiểm thử phần mềm xác nhận các thành phần như logic thời gian, API, start/stop, WebSocket và snapshot hoạt động đúng theo thiết kế. Nó chứng minh độ ổn định của mã nguồn, không chứng minh chất lượng nhận diện. Chất lượng model phải được đánh giá riêng bằng precision, recall, mAP và dữ liệu độc lập.”

---

# IV. Câu hỏi “gài” và cách trả lời an toàn

## 34. Nếu recall chỉ 47,33%, tại sao nhóm cho rằng đề tài thành công?

**Gợi ý trả lời:**

“Nhóm không cho rằng hệ thống đã thành công ở mức triển khai thực tế. Thành quả hiện tại là nguyên mẫu tích hợp hoạt động end-to-end và model mới cải thiện rõ rệt so với phiên bản cũ. Recall 47,33% chính là bằng chứng cho thấy nghiên cứu còn việc phải làm. Nhóm đánh giá kết quả theo đúng phạm vi nguyên mẫu, không nâng thành sản phẩm hoàn thiện.”

## 35. Tên đề tài nói giám sát gian lận, nhưng hệ thống chủ yếu phát hiện điện thoại — có quá rộng không?

**Gợi ý trả lời:**

“Đúng là tên đề tài rộng hơn phạm vi đã được đánh giá định lượng. Hiện phần có số liệu rõ nhất là phát hiện điện thoại; các tín hiệu tư thế mới ở mức luật hỗ trợ và chưa có đánh giá hành vi độc lập. Khi trình bày, nhóm giới hạn kết luận ở phạm vi nguyên mẫu và xem nhận diện hành vi đầy đủ là hướng phát triển.”

## 36. Nhóm có đang biến hành vi bình thường như cúi đầu viết bài thành gian lận không?

**Gợi ý trả lời:**

“Không. Cúi đầu chỉ tạo một tín hiệu có trọng số thấp và không phải kết luận. Chính video viết bài được đưa vào pilot để quan sát loại nhầm này. Trong ứng dụng thực tế, quy tắc cần được hiệu chỉnh theo môn thi và luôn phải có giám thị xác minh.”

## 37. Nếu hệ thống bỏ sót điện thoại thì ai chịu trách nhiệm?

**Gợi ý trả lời:**

“Vì hệ thống chỉ là công cụ hỗ trợ, giám sát chính vẫn thuộc quy trình coi thi và con người. Khi triển khai, phải công bố rõ giới hạn, không để người dùng hiểu rằng hệ thống bảo đảm phát hiện mọi trường hợp. Về kỹ thuật, nhóm cần theo dõi tỷ lệ bỏ sót và thiết lập cơ chế báo lỗi thiết bị hoặc model.”

## 38. Tại sao hội đồng nên đánh giá cao một hệ thống chưa thể triển khai?

**Gợi ý trả lời:**

“Giá trị nghiên cứu không chỉ nằm ở sản phẩm cuối mà còn ở quy trình kiểm chứng. Nhóm đã xây dựng được pipeline có thể chạy lại, lưu nguồn checkpoint, điều kiện đo, cảnh báo và minh chứng; đồng thời chỉ rõ các trường hợp thất bại. Đây là nền tảng có thể tiếp tục cải tiến bằng dữ liệu phòng thi thay vì một bản demo không đo được giới hạn.”

## 39. Nếu có thêm thời gian, nhóm có đảm bảo đạt trên 90% không?

**Gợi ý trả lời:**

“Nhóm không thể cam kết một tỷ lệ khi chưa có dữ liệu và quy trình đánh giá tương ứng. Mục tiêu phù hợp là xây tập test độc lập, xác định ngưỡng chấp nhận cùng giám thị, sau đó cải tiến và đo lại. Chỉ khi có kết quả mới, nhóm mới có thể kết luận hệ thống đạt mức nào.”

## 40. Có thể triển khai hệ thống ngay cho kỳ thi sắp tới không?

**Gợi ý trả lời:**

“Chưa nên. Hệ thống cần được thử nghiệm có kiểm soát, hoàn thiện đánh giá nhiều người, giảm cảnh báo nhầm, đo tải dài hạn và bổ sung quy trình bảo mật. Nếu thử tiếp, chỉ nên triển khai ở dạng pilot có giám sát, không dùng làm căn cứ duy nhất để xử lý thí sinh.”

---

# V. Những câu không nên trả lời quá mức

| Nếu được hỏi | Không nên nói | Nên nói |
|---|---|---|
| Độ chính xác | “Hệ thống chính xác 100%” | “Model đạt P 61,39%, R 47,33%, F1 53,45% trên validation” |
| Phòng thi thật | “Đã sẵn sàng triển khai” | “Mới pilot một người, một camera” |
| 4/4 episode | “Không bỏ sót điện thoại” | “Không bỏ sót bốn episode của bộ pilot nhỏ theo nhãn sơ bộ” |
| Điểm rủi ro | “Xác suất gian lận” | “Điểm heuristic để sắp xếp mức chú ý” |
| Quay đầu/cúi đầu | “Đây là hành vi gian lận” | “Đây là tín hiệu để giám thị kiểm tra” |
| GPU Colab | “Chắc chắn dùng T4/RTX 3060” | “Lượt train dùng GPU device 0; loại GPU chưa có log xác minh” |
| Hiệu năng | “Chạy thời gian thực” | “Đạt 9,65–10,95 FPS trên máy CPU thử nghiệm” |

# VI. Năm câu trả lời cần học thuộc

1. **“ExamGuard hỗ trợ giám thị sàng lọc thời điểm cần chú ý; hệ thống không tự kết luận gian lận.”**
2. **“Phạm vi hiện tại là nguyên mẫu một người, một camera; chưa thử nghiệm trong phòng thi thật.”**
3. **“Model điện thoại đạt precision 61,39%, recall 47,33% và F1 53,45% trên 214 ảnh validation.”**
4. **“Kết quả 4/4 episode thuộc một pilot nhỏ và đi kèm 6 cảnh báo ngoài khoảng nhãn, nên không thể gọi là accuracy 100%.”**
5. **“Nội dung nào chưa có dữ liệu, nhóm xin ghi nhận là chưa đủ cơ sở kết luận và xác định đó là bước đánh giá tiếp theo.”**
