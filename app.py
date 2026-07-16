import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Order Nhà Hàng", layout="wide")

# Thực đơn cố định
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

# Khởi tạo Session State để lưu dữ liệu tạm thời
if 'order_dict' not in st.session_state:
    st.session_state.order_dict = {}
if "history" not in st.session_state:
    st.session_state.history = []

# Thanh điều hướng Sidebar
page = st.sidebar.selectbox(
    "📋 Chọn trang",
    ["🍽️ Order", "🔑 Admin"]
)

# ==========================================
# TRANG ORDER (Dành cho Khách hàng / Nhân viên phục vụ)
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
# TRANG ADMIN (Dành cho Quản lý)
# ==========================================
elif page == "🔑 Admin":
    st.title("🔑 Trang Quản Trị Hệ Thống")

    password = st.text_input("Nhập mật khẩu", type="password")

    if password != "123456":
        st.warning("Vui lòng nhập đúng mật khẩu để truy cập.")
        st.stop()

    st.success("Đăng nhập thành công!")

    # Chia trang Admin thành 3 Tabs cho gọn gàng và bảo mật
    tab1, tab2, tab3 = st.tabs([
        "📋 Danh sách thực đơn", 
        "💰 Doanh thu & Lịch sử", 
        "📊 Biểu đồ thống kê bán hàng"
    ])

    with tab1:
        st.subheader("Menu hiện tại của nhà hàng")
        data = []
        for category in menu:
            for item, price in menu[category].items():
                data.append([category, item, price])

        df_menu = pd.DataFrame(data, columns=["Loại", "Tên món", "Giá"])
        st.dataframe(df_menu, use_container_width=True)

    with tab2:
        st.subheader("Doanh thu dựa trên hóa đơn đã thanh toán")
        if st.session_state.history:
            df_history = pd.DataFrame(st.session_state.history)
            tong_doanh_thu = df_history["Thành tiền"].sum()

            st.metric("Tổng doanh thu tích lũy", f"{tong_doanh_thu:,.0f} VNĐ")
            st.subheader("Danh sách lịch sử giao dịch")
            st.dataframe(df_history, use_container_width=True)
        else:
            st.info("Chưa có doanh thu nào được ghi nhận.")

    with tab3:
        st.subheader("Biểu đồ thống kê lượng bán từng món ăn")
        if st.session_state.history:
            history_df = pd.DataFrame(st.session_state.history)
            
            # Groupby để tính tổng số lượng đã bán của từng món
            summary = history_df.groupby("Tên món")["Số lượng"].sum().reset_index()
            
            # Hiển thị bảng số liệu tóm tắt
            st.dataframe(summary, use_container_width=True)
            
            # Vẽ biểu đồ cột trực quan sử dụng cột 'Tên món' làm nhãn trục X
            st.bar_chart(summary.set_index("Tên món")["Số lượng"])
        else:
            st.info("Chưa có dữ liệu giao dịch để hiển thị biểu đồ.")
