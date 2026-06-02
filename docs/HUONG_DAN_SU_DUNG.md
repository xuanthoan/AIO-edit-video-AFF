# AUTO VIDEO AFF

Hướng Dẫn Sử Dụng

## 1. Giới thiệu

AutoVideoAFF là phần mềm chỉnh sửa video hàng loạt dành cho Affiliate Marketing, TikTok, Facebook Reels và Shopee Video.

Phần mềm giúp bạn tạo nhiều phiên bản video khác nhau từ video gốc, thêm hình ảnh, chữ, highlight, sticker và watermark để phục vụ bán hàng, quảng cáo sản phẩm và làm nội dung mạng xã hội.

Các chức năng chính:

* Shuffle video
* Scene detect
* Auto fallback cut
* Chèn ảnh
* Chèn watermark
* Chèn text
* Chèn highlight
* Chèn sticker
* Render hàng loạt video

---

## 2. Cài đặt

Yêu cầu:

* Windows 10/11
* FFmpeg nếu bản phần mềm bạn dùng yêu cầu cài riêng
* Không yêu cầu cài Python khi dùng bản EXE

Cách sử dụng bản EXE:

1. Mở thư mục chứa phần mềm.
2. Bấm đúp vào file `AutoVideoAFF.exe`.
3. Nếu Windows hỏi xác nhận, chọn cho phép mở ứng dụng.
4. Bắt đầu thêm video và chỉnh sửa.

Lưu ý:

* Nếu phần mềm báo thiếu FFmpeg, hãy kiểm tra lại gói cài đặt hoặc liên hệ người cung cấp phần mềm.
* Không nên đổi tên hoặc xóa các thư mục đi kèm phần mềm nếu bạn dùng bản đóng gói sẵn.

---

## 3. Giao diện phần mềm

Giao diện AutoVideoAFF được chia thành 3 khu vực chính: cột trái, khu vực giữa và cột phải.

### Cột trái

Cột trái dùng để quản lý video và xem log xử lý.

* Thêm video
* Xóa video
* Danh sách video
* Log

Ý nghĩa:

* **Thêm video**: chọn một hoặc nhiều video cần xử lý.
* **Xóa video**: xóa video đang chọn khỏi danh sách.
* **Danh sách video**: hiển thị toàn bộ video đang chờ render.
* **Log**: hiển thị tiến trình, thông báo lỗi và trạng thái render.

### Khu vực giữa

Khu vực giữa dùng để xem trước nội dung video và chỉnh thời gian hiển thị overlay.

* Preview video
* Preview text
* Preview highlight
* Preview sticker
* Timeline

Ý nghĩa:

* **Preview video**: xem trước video đang chọn.
* **Preview text**: xem chữ hiển thị trên video.
* **Preview highlight**: xem các nhãn nổi bật như CTA, khuyến mãi, sale.
* **Preview sticker**: xem sticker đã chọn.
* **Timeline**: điều chỉnh thời điểm xuất hiện của text, highlight và sticker.

### Cột phải

Cột phải là nơi chọn pipeline và thiết lập các hiệu ứng.

#### Pipeline

Có 4 pipeline chính:

**Pipeline 1 — Shuffle + Image**

Dùng khi bạn muốn đảo cảnh video và chèn thêm ảnh, nhưng không cần thêm text, highlight hoặc sticker.

**Pipeline 2 — Shuffle + Image + Overlay**

Dùng khi bạn muốn làm video đầy đủ nhất: shuffle video, chèn ảnh, thêm watermark, text, highlight và sticker.

**Pipeline 3 — Shuffle + Overlay**

Dùng khi bạn muốn đảo cảnh video và thêm overlay, nhưng không cần chèn ảnh.

**Pipeline 4 — Overlay Only**

Dùng khi bạn muốn giữ nguyên video gốc và chỉ thêm watermark, text, highlight hoặc sticker.

#### Shuffle

* Sensitivity
* Fallback Minimum
* Fallback Maximum

Ý nghĩa:

* **Sensitivity**: độ nhạy khi phần mềm tự phát hiện cảnh. Số càng cao thì phần mềm càng khó cắt cảnh nhỏ.
* **Fallback Minimum**: thời lượng ngắn nhất của đoạn cắt tự động khi không phát hiện được cảnh.
* **Fallback Maximum**: thời lượng dài nhất của đoạn cắt tự động khi không phát hiện được cảnh.

#### Image

* Choose Images
* Crop Focus
* Image Height
* Overlap
* Fade Curve

Ý nghĩa:

* **Choose Images**: chọn ảnh để chèn vào video.
* **Crop Focus**: chọn vùng ưu tiên khi ảnh bị cắt, ví dụ trên, giữa hoặc dưới.
* **Image Height**: chiều cao phần ảnh so với khung video.
* **Overlap**: độ chồng giữa ảnh và video.
* **Fade Curve**: kiểu chuyển mờ giữa ảnh và video.

#### Watermark

* Watermark Text
* Font
* Font Size
* Font Color
* Opacity

Ý nghĩa:

* **Watermark Text**: nội dung watermark, ví dụ tên shop, tài khoản TikTok hoặc thương hiệu.
* **Font**: kiểu chữ của watermark.
* **Font Size**: kích thước chữ watermark.
* **Font Color**: màu chữ watermark.
* **Opacity**: độ mờ của watermark. Số thấp thì watermark mờ hơn.

#### Text

* Text
* Template
* Font Size
* Animation
* Motion Speed
* Motion Strength

Ý nghĩa:

* **Text**: nội dung chữ muốn hiển thị trên video.
* **Template**: mẫu màu và nền chữ.
* **Font Size**: kích thước chữ.
* **Animation**: hiệu ứng chuyển động của chữ.
* **Motion Speed**: tốc độ chuyển động.
* **Motion Strength**: độ mạnh của hiệu ứng chuyển động.

#### Highlight

* Highlight Text
* Highlight Font Size
* Style
* Animation

Ý nghĩa:

* **Highlight Text**: nội dung nổi bật, ví dụ “SALE 50%”, “MUA NGAY”, “HOT TREND”.
* **Highlight Font Size**: kích thước chữ highlight.
* **Style**: kiểu thiết kế highlight.
* **Animation**: hiệu ứng chuyển động của highlight.

#### Sticker

* Choose Sticker
* Scale
* Rotation
* Animation

Ý nghĩa:

* **Choose Sticker**: chọn hình sticker để chèn vào video.
* **Scale**: phóng to hoặc thu nhỏ sticker.
* **Rotation**: xoay sticker.
* **Animation**: hiệu ứng chuyển động của sticker.

---

## 4. Quy trình làm video cơ bản

### Bước 1: Thêm video

Bấm nút thêm video, sau đó chọn video cần xử lý. Bạn có thể thêm nhiều video để render hàng loạt.

### Bước 2: Chọn Pipeline

Chọn pipeline phù hợp với mục đích làm video.

Gợi ý:

* Nếu làm video TikTok Affiliate đầy đủ, nên chọn **Pipeline 2 — Shuffle + Image + Overlay**.
* Nếu chỉ muốn thêm chữ và sticker vào video gốc, chọn **Pipeline 4 — Overlay Only**.

### Bước 3: Cấu hình Shuffle

Điều chỉnh Sensitivity, Fallback Minimum và Fallback Maximum nếu bạn dùng pipeline có shuffle.

Nếu không chắc nên chọn gì, có thể giữ thông số mặc định.

### Bước 4: Chọn ảnh

Nếu pipeline có Image, bấm **Choose Images** để chọn ảnh sản phẩm hoặc ảnh minh họa.

### Bước 5: Thêm watermark

Nhập tên shop, tên thương hiệu hoặc tài khoản của bạn vào phần Watermark Text.

Nên để watermark mờ vừa phải để không che nội dung video.

### Bước 6: Thêm text

Nhập câu chữ ngắn, rõ ràng, dễ đọc.

Ví dụ:

* “Áo mặc siêu tôn dáng”
* “Deal hôm nay quá tốt”
* “Sản phẩm bán chạy”

### Bước 7: Thêm highlight

Thêm các câu nổi bật để thu hút người xem.

Ví dụ:

* “SALE 50%”
* “MUA NGAY”
* “HOT TREND”
* “BEST SELLER”

### Bước 8: Thêm sticker

Chọn sticker phù hợp với sản phẩm. Sau đó kéo sticker đến vị trí mong muốn trên preview.

### Bước 9: Kiểm tra preview

Xem lại video ở khu vực preview.

Cần kiểm tra:

* Text có dễ đọc không
* Highlight có bị che không
* Sticker có đúng vị trí không
* Watermark có quá đậm không
* Timeline hiển thị đúng thời điểm chưa

### Bước 10: Render Video

Bấm **Render Video** để xuất video.

Khi render xong, mở thư mục output để lấy video hoàn chỉnh.

---

## 5. Hướng dẫn Highlight

Highlight là phần chữ nổi bật dùng để nhấn mạnh ưu đãi, lời kêu gọi hành động hoặc điểm mạnh của sản phẩm.

Các kiểu highlight thường dùng:

### TikTok Bold

Dùng cho chữ ngắn, mạnh, dễ nhìn.

Nên dùng khi muốn tạo cảm giác giống video TikTok bán hàng.

Ví dụ:

* “HOT TREND”
* “MUA NGAY”
* “ĐANG GIẢM GIÁ”

### Blue Tag SVG

Dùng cho lời kêu gọi hành động hoặc thông tin cần nổi bật nhưng vẫn gọn gàng.

Phù hợp với:

* CTA
* Thông báo freeship
* Nhấn mạnh tính năng sản phẩm

Ví dụ:

* “MUA NGAY”
* “FREESHIP”
* “XEM GIÁ HÔM NAY”

### Orange Tag SVG

Dùng cho khuyến mãi, giảm giá và các nội dung cần tạo cảm giác gấp.

Phù hợp với:

* Sale
* Flash sale
* Mã giảm giá
* Deal trong ngày

Ví dụ:

* “SALE 50%”
* “DEAL SỐC”
* “GIẢM HÔM NAY”

### Fashion Streetwear

Dùng cho sản phẩm thời trang, outfit, phụ kiện và phong cách trẻ trung.

Phù hợp với:

* Quần áo
* Túi xách
* Giày dép
* Phụ kiện thời trang

Ví dụ:

* “OUTFIT ĐỈNH”
* “FORM SIÊU XỊN”
* “MẶC CỰC ĐẸP”

### Sticker Beauty SVG 1

Dùng cho sản phẩm làm đẹp, mỹ phẩm hoặc nội dung cần cảm giác mềm mại, bắt mắt.

Phù hợp với:

* Son môi
* Kem dưỡng
* Serum
* Đồ skincare

### Sticker Beauty SVG 2

Dùng khi muốn highlight trông nổi bật hơn, phù hợp video review sản phẩm đẹp, sang hoặc nữ tính.

Phù hợp với:

* Mỹ phẩm
* Thời trang nữ
* Phụ kiện làm đẹp

### Sticker Beauty SVG 3

Dùng cho nội dung cần nhấn mạnh mạnh hơn trong nhóm beauty hoặc fashion.

Phù hợp với:

* Video review nhanh
* Video chốt đơn
* Video giới thiệu ưu đãi

Mẹo sử dụng highlight:

* Nên dùng câu ngắn dưới 8 từ.
* Không nên để quá nhiều highlight cùng lúc.
* Nên đặt highlight ở vùng dễ nhìn, tránh che mặt người hoặc sản phẩm chính.

---

## 6. Hướng dẫn Sticker

Sticker giúp video sinh động hơn và tăng sự chú ý của người xem.

Cách dùng sticker:

### Chọn sticker

Bấm **Choose Sticker**, sau đó chọn file sticker từ máy tính.

Nên dùng sticker nền trong suốt nếu có, ví dụ file PNG.

### Thay đổi vị trí

Sau khi chọn sticker, bạn có thể kéo sticker trên khung preview đến vị trí mong muốn.

Gợi ý:

* Đặt sticker gần sản phẩm.
* Không đặt sticker che mặt người.
* Không đặt sticker che chữ quan trọng.

### Scale

Dùng Scale để phóng to hoặc thu nhỏ sticker.

Gợi ý:

* Sticker CTA nên vừa phải, dễ nhìn.
* Sticker trang trí không nên quá lớn.

### Rotation

Dùng Rotation để xoay sticker.

Xoay nhẹ có thể giúp video tự nhiên hơn, nhưng không nên xoay quá nhiều làm khó nhìn.

### Animation

Dùng Animation để thêm chuyển động cho sticker.

Một số kiểu dễ dùng:

* Pop
* Bounce
* Fade In
* Slide Up
* Rotate Float

---

## 7. Hướng dẫn Render

### Render Video

Bấm **Render Video** để bắt đầu xuất video.

Trước khi render, nên kiểm tra:

* Đã thêm video chưa
* Đã chọn đúng pipeline chưa
* Đã chọn ảnh nếu pipeline cần ảnh chưa
* Text, highlight và sticker đã đúng vị trí chưa
* Timeline đã đúng thời gian chưa

### Stop Render

Bấm **Stop** nếu muốn dừng render.

Dùng khi:

* Chọn nhầm video
* Chọn sai pipeline
* Muốn chỉnh lại nội dung trước khi xuất

### Open Output Folder

Bấm **Open Output Folder** để mở thư mục chứa video đã xuất.

Thông thường, video xuất ra sẽ nằm trong thư mục `output`.

---

## 8. Các lỗi thường gặp

### Không render được

Nguyên nhân:

* Thiếu video
* Thiếu ảnh
* Chưa chọn đúng pipeline
* Thiếu FFmpeg trong một số bản cài đặt

Cách xử lý:

* Kiểm tra danh sách video ở cột trái.
* Nếu dùng pipeline có Image, hãy chọn ảnh trước khi render.
* Xem phần Log để biết lỗi cụ thể.
* Nếu báo thiếu FFmpeg, hãy kiểm tra lại bộ cài hoặc liên hệ người cung cấp phần mềm.

### Không thấy highlight

Nguyên nhân:

* Highlight đang bị tắt
* Chưa nhập Highlight Text
* Highlight nằm ngoài thời gian hiển thị trên timeline
* Highlight bị che hoặc nằm ngoài vùng dễ nhìn

Cách xử lý:

* Nhập nội dung highlight.
* Kiểm tra lại style và animation.
* Kiểm tra timeline.
* Kéo highlight về vị trí dễ nhìn trên preview.

### Không thấy sticker

Nguyên nhân:

* Chưa chọn sticker
* Sticker đang nằm ngoài thời gian hiển thị
* Sticker quá nhỏ
* Sticker nằm ngoài vùng preview

Cách xử lý:

* Bấm **Choose Sticker** để chọn sticker.
* Tăng Scale nếu sticker quá nhỏ.
* Kiểm tra timeline.
* Kéo sticker về giữa vùng video.

### Video xuất ra khác preview

Nguyên nhân:

* Chưa cập nhật phiên bản mới
* Preview chỉ là bản xem nhanh
* Một số hiệu ứng khi render có thể cần kiểm tra lại bằng video xuất thật

Cách xử lý:

* Cập nhật phiên bản mới nhất nếu có.
* Render thử một video ngắn trước khi render hàng loạt.
* Kiểm tra lại font, vị trí chữ và hiệu ứng.

---

## 9. Mẹo sử dụng

* Dùng Pipeline 2 cho TikTok Affiliate.
* Dùng Highlight ngắn dưới 8 từ.
* Dùng Sticker Beauty cho sản phẩm thời trang, mỹ phẩm và làm đẹp.
* Dùng Blue Tag cho CTA như “MUA NGAY”, “XEM GIÁ”, “FREESHIP”.
* Dùng Orange Tag cho khuyến mãi như “SALE 50%”, “DEAL SỐC”, “GIẢM HÔM NAY”.
* Không nên dùng quá nhiều chữ trong một video.
* Nên render thử 1 video trước khi render hàng loạt.
* Nên dùng watermark mờ để bảo vệ video nhưng không gây khó chịu cho người xem.
* Nên kiểm tra preview trước khi bấm render.

---

## 10. Thông tin phiên bản

Tác giả: Nguyễn Xuân Thoán

Version: 1.0

AutoVideoAFF

Batch Video Production Software
