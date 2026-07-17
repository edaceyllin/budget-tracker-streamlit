import pandas as pd
import plotly.express as px
import streamlit as st
import json
import os
from datetime import datetime
def veri_yukle():
    if os.path.exists("veriler.json"):
        with open("veriler.json", "r", encoding="utf-8") as dosya:
            return json.load(dosya)
    return {"Gelirler": [], "Giderler": []}


def veri_kaydet(veriler):
    with open("veriler.json", "w", encoding="utf-8") as dosya:
        json.dump(veriler, dosya, indent=4, ensure_ascii=False)


veriler = veri_yukle()
Gelirler = veriler.get("Gelirler", [])
Giderler = veriler.get("Giderler", [])

st.title("Bütçe Takip Uygulaması")
st.sidebar.title("İşlemler")
menu = st.sidebar.radio(
    "Gitmek istediğiniz sayfayı seçin:",
    ["Ana Sayfa", "Gelir/Gider Ekle", "Kayıtları Listele", "Kayıtlarda Ara", "Kayıt Sil"]
)

if menu == "Ana Sayfa":
    st.header("Güncel Durum")
    toplam_gelir = sum(gelir[1] for gelir in Gelirler)
    toplam_gider = sum(gider[1] for gider in Giderler)
    bakiye = toplam_gelir - toplam_gider
    col1, col2, col3 = st.columns(3)
    col1.metric("Toplam Gelir", f"{toplam_gelir:.2f} ₺")
    col2.metric("Toplam Gider", f"{toplam_gider:.2f} ₺")
    col3.metric("Güncel Bakiye", f"{bakiye:.2f} ₺")
    if Giderler:
        df_gider = pd.DataFrame(
            Giderler,
            columns=["Açıklama", "Tutar", "Tarih", "Kategori"]
        )
        grafik = px.pie(
            df_gider,
            names="Kategori",
            values="Tutar",
            title="Giderlerin Kategori Dağılımı"
        )
        st.plotly_chart(grafik, use_container_width=True)
    else:
        st.info("Henüz gider kaydı yok.")
elif menu == "Gelir/Gider Ekle":
    st.header("Gelir/Gider Ekle")
    islem_turu = st.selectbox("İşlem Türü", ["Gelir", "Gider"])

    aciklama = st.text_input("Açıklama")
    tutar = st.number_input("Tutar (₺)", min_value=0.0, format="%.2f")
    tarih = st.date_input("Tarih")

    if islem_turu == "Gelir":
        kategoriler = ["Maaş", "Burs", "Freelance", "Yatırım", "Diğer"]
    else:
        kategoriler = ["Market", "Yemek", "Ulaşım", "Fatura", "Kira", "Sağlık", "Eğlence", "Diğer"]

    kategori = st.selectbox("Kategori", kategoriler)

    kaydedildi = st.button("Kaydet")
    if kaydedildi:
        if aciklama == "" or tutar == 0.0:
            st.error("Alanları doldurun.")
        else:
            tarih_str = tarih.strftime("%Y-%m-%d")

            if islem_turu == "Gelir":
                Gelirler.append([aciklama, tutar, tarih_str, kategori])
            else:
                Giderler.append([aciklama, tutar, tarih_str, kategori])

            veriler["Gelirler"] = Gelirler
            veriler["Giderler"] = Giderler

            veri_kaydet(veriler)
            st.success("Kaydedildi.")
elif menu == "Kayıtları Listele":
    st.header("Geçmiş Kayıtlar")

    st.subheader("Gelirler")
    if Gelirler:
        df_gelir = pd.DataFrame(
            Gelirler,
            columns=["Açıklama", "Tutar", "Tarih", "Kategori"]
        )
        st.dataframe(df_gelir, use_container_width=True)
    else:
        st.info("Henüz gelir kaydı yok.")

    st.subheader("Giderler")
    if Giderler:
        df_gider = pd.DataFrame(
            Giderler,
            columns=["Açıklama", "Tutar", "Tarih", "Kategori"]
        )
        st.dataframe(df_gider, use_container_width=True)
    else:
        st.info("Henüz gider kaydı yok.")
    
    if Gelirler:
        df_gelir = pd.DataFrame(
            Gelirler,
            columns=["Açıklama", "Tutar", "Tarih", "Kategori"]
        )
        grafik_gelir = px.line(
            df_gelir,
            x="Tarih",
            y="Tutar",
            title="Gelirlerin Zaman İçindeki Değişimi"
        )
        df_gelir_kategori = (
            df_gelir.groupby("Kategori", as_index=False)["Tutar"]
            .sum()
        )
        grafik_gelir_cat = px.bar(
            df_gelir_kategori,
            x="Kategori",
            y="Tutar",
            title="Gelirlerin Kategori Toplamları"
        )
        
        st.plotly_chart(grafik_gelir_cat, use_container_width=True)
        df_gelir.to_excel("gelirler.xlsx", index=False)
        with open("gelirler.xlsx", "rb") as f:
            st.download_button(
                label="Gelirleri Excel Olarak İndir",
                data=f,
                file_name="gelirler.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    if Giderler:
        df_gider = pd.DataFrame(
            Giderler,
            columns=["Açıklama", "Tutar", "Tarih", "Kategori"]
        )
        grafik_gider = px.line(
            df_gider,
            x="Tarih",
            y="Tutar",
            title="Giderlerin Zaman İçindeki Değişimi"
        )
        st.plotly_chart(grafik_gider, use_container_width=True)
        df_gider_kategori = (
            df_gider.groupby("Kategori", as_index=False)["Tutar"]
            .sum()
        )
        grafik_gider_cat = px.bar(
            df_gider_kategori,
            x="Kategori",
            y="Tutar",
            title="Giderlerin Kategori Toplamları"
        )
        st.plotly_chart(grafik_gider_cat, use_container_width=True)
        df_gider.to_excel("giderler.xlsx", index=False)
        with open("giderler.xlsx", "rb") as f:
            st.download_button(
                label="Giderleri Excel Olarak İndir",
                data=f,
                file_name="giderler.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

elif menu == "Kayıtlarda Ara":
    st.header("Arama")
    arama_turu = st.selectbox("Tür", ["Gelir", "Gider"])
    kelime = st.text_input("Kelime:")
    if st.button("Ara"):
        liste = Gelirler if arama_turu == "Gelir" else Giderler
        sonuc = [x for x in liste if kelime.lower() in x[0].lower()]
        st.write(sonuc)

elif menu == "Kayıt Sil":
    st.header("Silme")
    silme_turu = st.selectbox("Tür", ["Gelir", "Gider"])
    liste = Gelirler if silme_turu == "Gelir" else Giderler
    secilen = st.selectbox("Seç:", [f"{i}: {x[0]}" for i, x in enumerate(liste)])
    if st.button("Sil"):
        if liste:
            indeks = int(secilen.split(":")[0])
            liste.pop(indeks)
            veriler["Gelirler" if silme_turu == "Gelir" else "Giderler"] = liste
            veri_kaydet(veriler)
            st.experimental_rerun()


