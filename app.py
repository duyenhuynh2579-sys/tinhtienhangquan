if page == "🔑 Admin":

    st.title("🔑 Trang Quản Trị")

    password = st.text_input("Nhập mật khẩu", type="password")

    if password != "123456":
        st.warning("Vui lòng nhập đúng mật khẩu.")
        st.stop()

    st.success("Đăng nhập thành công!")

    st.subheader("📋 Danh sách thực đơn")

    data = []

    for category in menu:
        for item, price in menu[category].items():
            data.append([category, item, price])

    df_menu = pd.DataFrame(
        data,
        columns=["Loại", "Tên món", "Giá"]
    )

    st.dataframe(df_menu, use_container_width=True)

    st.subheader("💰 Doanh thu hôm nay")

    if st.session_state.order_dict:

        df = pd.DataFrame.from_dict(
            st.session_state.order_dict,
            orient="index"
        )

        revenue = df["Thành tiền"].sum()

        st.metric(
            "Tổng doanh thu",
            f"{revenue:,.0f} VNĐ"
        )

        st.dataframe(df)

    else:
        st.info("Chưa có đơn hàng.")
