import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Order Nhà Hàng & Analytics", layout="wide")

menu = {
    "Đồ ăn": {
        "Pizza Hải Sản": 150000, "Mì Ý Bò Bằm": 95000, "Burger Gà": 65000,
        "Salad Trộn": 50000, "Bít tết Bò Mỹ": 250000, "Sườn nướng BBQ": 180000,
        "Cánh gà chiên mắm": 75000, "Lẩu cá diêu hồng": 200000, "Lẩu Thái hải sản": 300000
    },
    "Thức uống": {
        "Coca Cola": 20000, "Trà Đào Cam Sả": 35000, "Cà Phê Sữa": 25000,
        "Nước Suối": 10000, "Sinh tố Bơ": 45000, "Nước ép cam": 40000,
        "Mojito chanh dây": 55000, "Bia Heineken": 30000
    }
}

if 'order_dict' not in st.session_state:
    st.session_state.order_dict = {}

# Tự động tạo dữ liệu mẫu nếu lịch sử trống để biểu đồ Admin trông sinh động và thực tế
if "history" not in st.session_state or len(st.session_state.history) == 0:
    mock_history = []
    now = datetime.now()
    flat_menu = []
    for cat, items in menu.items():
        for name, price in items.items():
            flat_menu.append((name, price))
            
    # Tạo 150 đơn hàng giả lập trong vòng 4 tháng qua
    for _ in range(150):
        # Chọn ngẫu nhiên một món
        item_name, item_price = random.choice(flat_menu)
        # Số lượng ngẫu nhiên từ 1 đến 5
        qty = random.randint(1, 5)
        # Giờ bán tập trung nhiều vào giờ trưa (11-13h) và chiều tối (18-21h)
        hour_weights = [1,1,1,1,1,1,2,3,5,6,4,8,12,10,5,4,6,12,18,15,8,4,2,1] # 24 tiếng
        hour = random.choices(range(24), weights=hour_weights, k=1)[0]
        # Ngày ngẫu nhiên trong vòng 120 ngày qua
        days_ago = random.randint(0, 120)
        order_time = now - timedelta(days=days_ago)
        order_time = order_time.replace(hour=hour, minute=random.randint(0, 59), second=random.randint(0, 59))
        
        mock_history.append({
            "Thời gian": order_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Bàn": f"Bàn {random.randint(1, 20)}",
            "Tên món": item_name,
            "Số lượng": qty,
            "Thành tiền": item_price * qty
        })
    st.session_state.history = mock_history

page = st.sidebar.selectbox(
    "📋 Chọn trang",
    ["🍽️ Order", "🔑 Admin"]
)

# ==========================================
# TRANG ORDER (Khách hàng / Nhân viên)
# ==========================================
if page == "🍽️ Order":
    st.title("🍽️ Hệ thống Order Nhà Hàng MR. BÌNH")

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.subheader("Chọn Món")
        table_number = st.selectbox(
            "🪑 Chọn số bàn",
            [f"Bàn {i}" for i in range(1, 21)]
        )
        category = st.selectbox("Chọn loại:", list(menu.keys()))
        item = st.selectbox("Chọn món:", list(menu[category].keys()))
        quantity = st.number_input("Số lượng:", min_value=1, step=1, value=1)
        
        if st.button("Thêm vào giỏ"):
            price = menu[category][item]

            if item in st.session_state.order_dict:
                st.session_state.order_dict[item]["Số lượng"] += quantity
                st.session_state.order_dict[item]["Thành tiền"] = (
                    st.session_state.order_dict[item]["Số lượng"] * price
                )
                st.session_state.order_dict[item]["Bàn"] = table_number
            else:
                st.session_state.order_dict[item] = {
                    "Bàn": table_number,
                    "Tên món": item,
                    "Đơn giá": price,
                    "Số lượng": quantity,
                    "Thành tiền": price * quantity
                }
            st.success(f"Đã thêm {item} vào giỏ!")
            st.rerun()

    with col2:
        st.subheader("Giỏ hàng hiện tại")

        if st.session_state.order_dict:
            df = pd.DataFrame.from_dict(st.session_state.order_dict, orient="index")
            st.table(df[["Bàn", "Tên món", "Đơn giá", "Số lượng", "Thành tiền"]])

            tam_tinh = df["Thành tiền"].sum()
            giam_gia = tam_tinh * 0.05 if tam_tinh > 1000000 else 0
            tong_thanh_toan = tam_tinh - giam_gia

            st.write(f"**Tạm tính:** {tam_tinh:,.0f} VNĐ")
            if giam_gia > 0:
                st.write(f"**Giảm giá (5% cho đơn > 1M):** -{giam_gia:,.0f} VNĐ")
            st.metric("Tổng thanh toán", f"{tong_thanh_toan:,.0f} VNĐ")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("💳 Thanh toán"):
                    for row in st.session_state.order_dict.values():
                        st.session_state.history.append({
                            "Thời gian": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Bàn": row["Bàn"],
                            "Tên món": row["Tên món"],
                            "Số lượng": row["Số lượng"],
                            "Thành tiền": row["Thành tiền"]
                        })
                    st.success("Thanh toán thành công!")
                    st.session_state.order_dict = {}
                    st.rerun()

            with col_btn2:
                if st.button("🗑️ Xóa giỏ hàng"):
                    st.session_state.order_dict = {}
                    st.rerun()
        else:
            st.info("Giỏ hàng đang trống.")

# ==========================================
# TRANG ADMIN (Quản lý & Thống kê thông minh)
# ==========================================
elif page == "🔑 Admin":
    st.title("🔑 Trang Quản Trị & Phân Tích Doanh Thu")

    password = st.text_input("Nhập mật khẩu", type="password")

    if password != "123456":
        st.warning("Vui lòng nhập đúng mật khẩu để truy cập dữ liệu kinh doanh.")
        st.stop()

    st.success("Đăng nhập thành công!")

    # Thiết lập các tab quản trị chuyên sâu
    tab1, tab2, tab3 = st.tabs([
        "📋 Danh sách thực đơn", 
        "💰 Doanh thu & Lịch sử", 
        "📊 Thống kê & Phân tích bán hàng chuyên sâu"
    ])

    # --- TAB 1: MENU ---
    with tab1:
        st.subheader("Menu hiện tại của nhà hàng")
        data = []
        for category in menu:
            for item, price in menu[category].items():
                data.append([category, item, price])

        df_menu = pd.DataFrame(data, columns=["Loại", "Tên món", "Giá"])
        st.dataframe(df_menu, use_container_width=True)

    # --- TAB 2: DOANH THU LỊCH SỬ ---
    with tab2:
        st.subheader("Doanh thu dựa trên hóa đơn đã thanh toán")
        if st.session_state.history:
            df_history = pd.DataFrame(st.session_state.history)
            tong_doanh_thu = df_history["Thành tiền"].sum()

            col_met1, col_met2 = st.columns(2)
            col_met1.metric("Tổng doanh thu tích lũy", f"{tong_doanh_thu:,.0f} VNĐ")
            col_met2.metric("Tổng số đơn hàng thành công", f"{len(df_history)} món")

            st.subheader("Danh sách lịch sử giao dịch")
            st.dataframe(df_history, use_container_width=True)
        else:
            st.info("Chưa có doanh thu nào được ghi nhận.")

    # --- TAB 3: PHÂN TÍCH CHUYÊN SÂU ---
    with tab3:
        st.subheader("📊 Biểu đồ Phân tích & Báo cáo Kinh doanh")
        
        if st.session_state.history:
            # Chuyển đổi dữ liệu lịch sử sang DataFrame
            df_anal = pd.DataFrame(st.session_state.history)
            df_anal["Thời gian"] = pd.to_datetime(df_anal["Thời gian"])
            
            # Trích xuất thông tin thời gian để phân tích
            df_anal["Giờ"] = df_anal["Thời gian"].dt.hour
            df_anal["Tháng-Năm"] = df_anal["Thời gian"].dt.strftime("%m/%Y")
            df_anal["Tháng_Số"] = df_anal["Thời gian"].dt.month
            
            # 1. Tính toán KPIs tổng quan
            # Món bán chạy nhất
            best_seller = df_anal.groupby("Tên món")["Số lượng"].sum().idxmax()
            best_seller_qty = df_anal.groupby("Tên món")["Số lượng"].sum().max()
            
            # Giờ bán chạy nhất
            best_hour = df_anal.groupby("Giờ")["Số lượng"].sum().idxmax()
            best_hour_qty = df_anal.groupby("Giờ")["Số lượng"].sum().max()
            
            # Tháng bán chạy nhất
            best_month = df_anal.groupby("Tháng-Năm")["Thành tiền"].sum().idxmax()
            best_month_rev = df_anal.groupby("Tháng-Năm")["Thành tiền"].sum().max()
            
            # Hiển thị bộ ba thẻ KPI hàng đầu
            col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
            with col_kpi1:
                st.info("🏆 MÓN BÁN CHẠY NHẤT")
                st.metric(label=best_seller, value=f"{best_seller_qty} phần")
            with col_kpi2:
                st.warning("⚡ KHUNG GIỜ VÀNG (Đắt khách nhất)")
                st.metric(label=f"Khung giờ: {best_hour:02d}:00 - {(best_hour+1):02d}:00", value=f"{best_hour_qty} phần bán ra")
            with col_kpi3:
                st.success("📅 THÁNG DOANH THU ĐỈNH ĐIỂM")
                st.metric(label=f"Tháng {best_month}", value=f"{best_month_rev:,.0f} VNĐ")
                
            st.markdown("---")
            
            # PHÂN TÍCH 1: THỐNG KÊ CHI TIẾT THEO MÓN ĂN (Số lượng & Doanh thu)
            st.write("### 🍔 Doanh thu & Số lượng của từng món ăn")
            
            summary_món = df_anal.groupby("Tên món").agg(
                Số_lượng_bán=("Số lượng", "sum"),
                Doanh_thu=("Thành tiền", "sum")
            ).reset_index()
            
            summary_món = summary_món.sort_values(by="Số_lượng_bán", ascending=False)
            
            col_chart1, col_table1 = st.columns([1.5, 1])
            with col_chart1:
                st.write("**Biểu đồ so sánh lượng bán và doanh thu từng món:**")
                # Chuẩn bị dữ liệu hiển thị biểu đồ cột cho doanh thu (trục X là món ăn)
                chart_data = summary_món.set_index("Tên món")
                st.bar_chart(chart_data["Số_lượng_bán"])
                st.caption("Biểu đồ thể hiện Tổng Số Lượng Bán ra của từng món")
            with col_table1:
                st.write("**Bảng số liệu xếp hạng chi tiết:**")
                st.dataframe(
                    summary_món.style.format({"Doanh_thu": "{:,.0f} VNĐ"}),
                    use_container_width=True,
                    hide_index=True
                )
                
            st.markdown("---")
            
            # PHÂN TÍCH 2: THỐNG KÊ THEO KHUNG GIỜ (Món nào bán tốt nhất và thời điểm đông khách)
            st.write("### ⏰ Phân tích Khung giờ bán chạy nhất trong ngày")
            
            summary_giơ = df_anal.groupby("Giờ").agg(
                Số_lượng_món=("Số lượng", "sum"),
                Tổng_doanh_thu=("Thành tiền", "sum")
            ).reset_index()
            
            # Điền đầy đủ các giờ từ 0 đến 23 nếu chưa có dữ liệu để biểu đồ liền mạch
            all_hours = pd.DataFrame({"Giờ": range(24)})
            summary_giơ = pd.merge(all_hours, summary_giơ, on="Giờ", how="left").fillna(0)
            
            col_chart2, col_info2 = st.columns([1.8, 1])
            with col_chart2:
                st.write("**Biểu đồ lượng khách mua hàng theo các khung giờ (0h - 23h):**")
                # Vẽ biểu đồ cột phân bố lượng bán theo giờ
                st.bar_chart(summary_giơ.set_index("Giờ")["Số_lượng_món"])
            with col_info2:
                st.write("**Nhận xét & Gợi ý vận hành:**")
                st.markdown(f"""
                - **Khung giờ đông khách nhất:** **{best_hour:02d}:00 - {(best_hour+1):02d}:00** với tổng cộng **{best_hour_qty} món** được bán ra.
                - **Gợi ý nhân sự:** Nên bố trí thêm nhân viên phục vụ và chuẩn bị sẵn nguyên vật liệu trước khung giờ này 30 phút để tránh quá tải bếp.
                - **Khuyến mãi giờ thấp điểm:** Có thể áp dụng chương trình Happy Hour (Giảm giá hoặc tặng kèm nước uống) vào các khung giờ ít khách để kích cầu.
                """)
                st.dataframe(
                    summary_giơ[summary_giơ["Số_lượng_món"] > 0].style.format({"Tổng_doanh_thu": "{:,.0f} VNĐ"}),
                    use_container_width=True,
                    hide_index=True
                )
                
            st.markdown("---")
            
            # PHÂN TÍCH 3: BIẾN ĐỘNG DOANH THU THEO THÁNG
            st.write("### 📅 Biến động doanh thu và lượng bán theo Tháng")
            
            summary_tháng = df_anal.groupby(["Tháng_Số", "Tháng-Năm"]).agg(
                Số_lượng_bán=("Số lượng", "sum"),
                Doanh_thu=("Thành tiền", "sum")
            ).reset_index().sort_values("Tháng_Số")
            
            col_chart3, col_table3 = st.columns([1.5, 1])
            with col_chart3:
                st.write("**Biểu đồ cột xu hướng Doanh Thu qua các Tháng:**")
                st.bar_chart(summary_tháng.set_index("Tháng-Năm")["Doanh_thu"])
            with col_table3:
                st.write("**Bảng số liệu tổng hợp theo Tháng:**")
                st.dataframe(
                    summary_tháng[["Tháng-Năm", "Số_lượng_bán", "Doanh_thu"]].style.format({"Doanh_thu": "{:,.0f} VNĐ"}),
                    use_container_width=True,
                    hide_index=True
                )
                
        else:
            st.info("Chưa có dữ liệu lịch sử thanh toán nào để thực hiện phân tích thống kê.")
            st.info("Chưa có dữ liệu giao dịch để hiển thị biểu đồ.")
