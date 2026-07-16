import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Thiết lập cấu hình trang hiển thị rộng rãi, tối ưu trải nghiệm người dùng
st.set_page_config(page_title="Order Nhà Hàng & Real-time Analytics", layout="wide")

# Thực đơn chính thức của nhà hàng
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

# Khởi tạo giỏ hàng hiện tại (chưa thanh toán)
if 'order_dict' not in st.session_state:
    st.session_state.order_dict = {}

# Khởi tạo lịch sử đơn hàng trống hoàn toàn (Sẽ chỉ tăng lên khi có khách đặt và thanh toán thật)
if "history" not in st.session_state:
    st.session_state.history = []

# Tạo thanh điều hướng Sidebar
page = st.sidebar.selectbox(
    "📋 Chọn trang",
    ["🍽️ Order", "🔑 Admin"]
)

# ==========================================
# TRANG ORDER (Khách hàng / Nhân viên phục vụ)
# ==========================================
if page == "🍽️ Order":
    st.title("🍽️ Hệ thống Order Nhà Hàng")
    st.caption("Ghi nhận order nhanh chóng và chính xác theo thời gian thực")

    col1, col2 = st.columns([1, 1.3])

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

            # Nếu món đã có trong giỏ, cộng dồn số lượng
            if item in st.session_state.order_dict:
                st.session_state.order_dict[item]["Số lượng"] += quantity
                st.session_state.order_dict[item]["Thành tiền"] = (
                    st.session_state.order_dict[item]["Số lượng"] * price
                )
                st.session_state.order_dict[item]["Bàn"] = table_number
            else:
                # Nếu là món mới, thêm mới vào giỏ hàng
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
            # Giảm giá 5% cho các hóa đơn có giá trị lớn hơn 1,000,000 VNĐ
            giam_gia = tam_tinh * 0.05 if tam_tinh > 1000000 else 0
            tong_thanh_toan = tam_tinh - giam_gia

            st.write(f"**Tạm tính:** {tam_tinh:,.0f} VNĐ")
            if giam_gia > 0:
                st.write(f"**Giảm giá (5% cho đơn > 1M):** -{giam_gia:,.0f} VNĐ")
            st.metric("Tổng thanh toán thực tế", f"{tong_thanh_toan:,.0f} VNĐ")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("💳 Thanh toán"):
                    # Ghi nhận chính xác ngày giờ thật của hệ thống lúc bấm thanh toán
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    for row in st.session_state.order_dict.values():
                        st.session_state.history.append({
                            "Thời gian": now_str,
                            "Bàn": row["Bàn"],
                            "Tên món": row["Tên món"],
                            "Số lượng": row["Số lượng"],
                            "Thành tiền": row["Thành tiền"]
                        })
                    st.success("Thanh toán thành công! Dữ liệu đã được lưu vào hệ thống.")
                    # Giải phóng giỏ hàng sau khi thanh toán xong
                    st.session_state.order_dict = {}
                    st.rerun()

            with col_btn2:
                if st.button("🗑️ Xóa toàn bộ giỏ"):
                    st.session_state.order_dict = {}
                    st.rerun()
        else:
            st.info("Giỏ hàng đang trống. Hãy chọn món ăn/đồ uống bên trái để lên đơn.")

# ==========================================
# TRANG ADMIN (Quản lý & Thống kê thông minh)
# ==========================================
elif page == "🔑 Admin":
    st.title("🔑 Trang Quản Trị & Phân Tích Doanh Thu")

    password = st.text_input("Nhập mật khẩu quản trị", type="password")

    if password != "123456":
        st.warning("Vui lòng nhập mật khẩu chính xác để xem dữ liệu kinh doanh nhạy cảm.")
        st.stop()

    st.success("Xác thực thành công!")

    # Thiết lập các tab quản trị chuyên sâu độc quyền cho Admin
    tab1, tab2, tab3 = st.tabs([
        "📋 Danh sách thực đơn", 
        "💰 Doanh thu & Nhật ký giao dịch", 
        "📊 Thống kê & Phân tích bán hàng REAL-TIME"
    ])

    # --- TAB 1: DANH SÁCH THỰC ĐƠN ---
    with tab1:
        st.subheader("Menu hiện hành của nhà hàng")
        data = []
        for category in menu:
            for item, price in menu[category].items():
                data.append([category, item, price])

        df_menu = pd.DataFrame(data, columns=["Phân loại", "Tên món", "Đơn giá (VNĐ)"])
        st.dataframe(df_menu, use_container_width=True, hide_index=True)

    # --- TAB 2: NHẬT KÝ GIAO DỊCH THẬT ---
    with tab2:
        st.subheader("Doanh thu & Hóa đơn thực tế từ khách gọi")
        if st.session_state.history:
            df_history = pd.DataFrame(st.session_state.history)
            tong_doanh_thu = df_history["Thành tiền"].sum()

            col_met1, col_met2 = st.columns(2)
            col_met1.metric("Tổng doanh thu tích lũy (Real-time)", f"{tong_doanh_thu:,.0f} VNĐ")
            col_met2.metric("Số lượng món đã phục vụ", f"{df_history['Số lượng'].sum()} phần")

            st.subheader("Chi tiết lịch sử thanh toán thực tế")
            st.dataframe(df_history, use_container_width=True, hide_index=True)
        else:
            st.info("Hệ thống chưa ghi nhận bất kỳ giao dịch thanh toán nào từ khách hàng.")

    # --- TAB 3: BIỂU ĐỒ THỐNG KÊ CHI TIẾT ---
    with tab3:
        st.subheader("📊 Biểu đồ Thống kê Real-time")
        
        if st.session_state.history:
            # Chuyển đổi dữ liệu lịch sử khách đặt thật sang DataFrame
            df_anal = pd.DataFrame(st.session_state.history)
            df_anal["Thời gian"] = pd.to_datetime(df_anal["Thời gian"])
            
            # Trích xuất thời gian thật để phân tách phân tích
            df_anal["Giờ"] = df_anal["Thời gian"].dt.hour
            df_anal["Tháng-Năm"] = df_anal["Thời gian"].dt.strftime("%m/%Y")
            df_anal["Tháng_Số"] = df_anal["Thời gian"].dt.month
            
            # 1. Tính toán KPIs tổng quan dựa trên các hóa đơn thật
            best_seller = df_anal.groupby("Tên món")["Số lượng"].sum().idxmax()
            best_seller_qty = df_anal.groupby("Tên món")["Số lượng"].sum().max()
            
            best_hour = df_anal.groupby("Giờ")["Số lượng"].sum().idxmax()
            best_hour_qty = df_anal.groupby("Giờ")["Số lượng"].sum().max()
            
            best_month = df_anal.groupby("Tháng-Năm")["Thành tiền"].sum().idxmax()
            best_month_rev = df_anal.groupby("Tháng-Năm")["Thành tiền"].sum().max()
            
            # Hiển thị bộ ba thẻ KPI hàng đầu theo thời gian thực
            col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
            with col_kpi1:
                st.info("🏆 MÓN BÁN CHẠY NHẤT")
                st.metric(label=best_seller, value=f"{best_seller_qty} phần")
            with col_kpi2:
                st.warning("⚡ KHUNG GIỜ VÀNG (Đông khách nhất)")
                st.metric(label=f"Khung giờ: {best_hour:02d}:00 - {(best_hour+1):02d}:00", value=f"{best_hour_qty} phần")
            with col_kpi3:
                st.success("📅 THÁNG DOANH THU ĐỈNH ĐIỂM")
                st.metric(label=f"Tháng {best_month}", value=f"{best_month_rev:,.0f} VNĐ")
                
            st.markdown("---")
            
            # PHÂN TÍCH 1: BIỂU ĐỒ DOANH THU & SỐ LƯỢNG CỦA TỪNG MÓN ĂN
            st.write("### 🍔 Doanh thu & Số lượng tiêu thụ của từng món ăn")
            
            summary_mon = df_anal.groupby("Tên món").agg(
                Số_lượng_bán=("Số lượng", "sum"),
                Doanh_thu=("Thành tiền", "sum")
            ).reset_index()
            
            summary_mon = summary_mon.sort_values(by="Số_lượng_bán", ascending=False)
            
            col_chart1, col_table1 = st.columns([1.5, 1])
            with col_chart1:
                st.write("**Biểu đồ cột thể hiện Tổng số lượng bán ra:**")
                chart_data = summary_mon.set_index("Tên món")
                st.bar_chart(chart_data["Số_lượng_bán"])
            with col_table1:
                st.write("**Số liệu doanh thu thực tế từng món:**")
                st.dataframe(
                    summary_mon.style.format({"Doanh_thu": "{:,.0f} VNĐ"}),
                    use_container_width=True,
                    hide_index=True
                )
                
            st.markdown("---")
            
            # PHÂN TÍCH 2: PHÂN TÍCH KHUNG GIỜ KHÁCH ĐẶT TRONG NGÀY
            st.write("### ⏰ Thống kê lượng khách đặt theo Khung giờ (0h - 23h)")
            
            summary_gio = df_anal.groupby("Giờ").agg(
                Số_lượng_món=("Số lượng", "sum"),
                Doanh_thu=("Thành tiền", "sum")
            ).reset_index()
            
            # Tạo trục 24 tiếng đầy đủ để biểu đồ mượt mà
            all_hours = pd.DataFrame({"Giờ": range(24)})
            summary_gio = pd.merge(all_hours, summary_gio, on="Giờ", how="left").fillna(0)
            
            col_chart2, col_info2 = st.columns([1.5, 1])
            with col_chart2:
                st.write("**Biểu đồ lượng bán theo từng khung giờ trong ngày:**")
                st.bar_chart(summary_gio.set_index("Giờ")["Số_lượng_món"])
            with col_info2:
                st.write("**Thời điểm bán chạy nhất trong ngày:**")
                st.markdown(f"👉 Khung giờ đắt khách nhất hiện tại là từ **{best_hour:02d}:00 - {(best_hour+1):02d}:00** với tổng cộng **{best_hour_qty} phần** được thanh toán.")
                st.dataframe(
                    summary_gio[summary_gio["Số_lượng_món"] > 0].style.format({"Doanh_thu": "{:,.0f} VNĐ"}),
                    use_container_width=True,
                    hide_index=True
                )
                
            st.markdown("---")
            
            # PHÂN TÍCH 3: BIẾN ĐỘNG THEO THÁNG
            st.write("### 📅 Doanh thu bán hàng theo Tháng")
            
            summary_thang = df_anal.groupby(["Tháng_Số", "Tháng-Năm"]).agg(
                Số_lượng_bán=("Số lượng", "sum"),
                Doanh_thu=("Thành tiền", "sum")
            ).reset_index().sort_values("Tháng_Số")
            
            col_chart3, col_table3 = st.columns([1.5, 1])
            with col_chart3:
                st.write("**Biểu đồ cột tăng trưởng doanh thu qua các tháng:**")
                st.bar_chart(summary_thang.set_index("Tháng-Năm")["Doanh_thu"])
            with col_table3:
                st.write("**Tổng doanh thu chi tiết từng tháng:**")
                st.dataframe(
                    summary_thang[["Tháng-Năm", "Số_lượng_bán", "Doanh_thu"]].style.format({"Doanh_thu": "{:,.0f} VNĐ"}),
                    use_container_width=True,
                    hide_index=True
                )
                
        else:
            st.info("Chưa có dữ liệu giao dịch thực tế để hiển thị phân tích. Vui lòng thực hiện đặt món và Thanh toán ở trang 'Order' để hệ thống bắt đầu vẽ biểu đồ tự động.")
