import streamlit as st
import numpy as np
import pandas as pd
import skfuzzy as fuzz
import skfuzzy.control as ctrl
import matplotlib.pyplot as plt

# ----------------------------------------------------
# CONFIG & SAYFA BAŞLIĞI

st.set_page_config(page_title="Akıllı Klima Fan Kontrolörü", layout="wide")
st.title("Otomatik Akıllı Klima Fan Kontrol Sistemi")
st.caption("Bulanık Mantık Dönem Projesi")

# Proje Raporu İsterlerini Arayüze Sekme Olarak Ekleme 
tab_sistem, tab_rapor = st.tabs(["🎮 Kontrol Sistemi Arayüzü", "📝 Proje Tanımı & Değerlendirme Raporu"])

# ----------------------------------------------------
# FUZZY VARIABLES (EVRENSEL KÜMELER)

# En az 3 giriş ve 1 çıkış 
temperature = ctrl.Antecedent(np.arange(0, 51, 1), 'temperature')
humidity = ctrl.Antecedent(np.arange(0, 101, 1), 'humidity')
room_size = ctrl.Antecedent(np.arange(5, 101, 1), 'room_size')
fan_speed = ctrl.Consequent(np.arange(0, 101, 1), 'fan_speed')

# Üyelik Fonksiyonları - Her biri için 3 adet dilsel tanımlama (İster 6)
temperature['cold'] = fuzz.trimf(temperature.universe, [0, 0, 18])
temperature['normal'] = fuzz.trimf(temperature.universe, [15, 24, 32])
temperature['hot'] = fuzz.trimf(temperature.universe, [28, 50, 50])

humidity['dry'] = fuzz.trimf(humidity.universe, [0, 0, 40])
humidity['comfortable'] = fuzz.trimf(humidity.universe, [30, 55, 75])
humidity['humid'] = fuzz.trimf(humidity.universe, [65, 100, 100])

room_size['small'] = fuzz.trimf(room_size.universe, [5, 5, 25])
room_size['medium'] = fuzz.trimf(room_size.universe, [20, 45, 70])
room_size['large'] = fuzz.trimf(room_size.universe, [60, 100, 100])

# Durulaştırma yöntemi olarak Ağırlık Merkezi (Centroid) seçildi (Tasarım İsteri e)
fan_speed.defuzzify_method = 'centroid'
fan_speed['low'] = fuzz.trimf(fan_speed.universe, [0, 0, 40])
fan_speed['medium'] = fuzz.trimf(fan_speed.universe, [30, 50, 70])
fan_speed['high'] = fuzz.trimf(fan_speed.universe, [60, 100, 100])

# ----------------------------------------------------
# KURAL TABANI (27 ADET KURAL)

rules = [
    # --- TEMPERATURE: COLD (9 Kural) ---
    ctrl.Rule(temperature['cold'] & humidity['dry'] & room_size['small'], fan_speed['low']),
    ctrl.Rule(temperature['cold'] & humidity['dry'] & room_size['medium'], fan_speed['low']),
    ctrl.Rule(temperature['cold'] & humidity['dry'] & room_size['large'], fan_speed['medium']),
    
    ctrl.Rule(temperature['cold'] & humidity['comfortable'] & room_size['small'], fan_speed['low']),
    ctrl.Rule(temperature['cold'] & humidity['comfortable'] & room_size['medium'], fan_speed['medium']),
    ctrl.Rule(temperature['cold'] & humidity['comfortable'] & room_size['large'], fan_speed['medium']),
    
    ctrl.Rule(temperature['cold'] & humidity['humid'] & room_size['small'], fan_speed['medium']),
    ctrl.Rule(temperature['cold'] & humidity['humid'] & room_size['medium'], fan_speed['medium']),
    ctrl.Rule(temperature['cold'] & humidity['humid'] & room_size['large'], fan_speed['high']),

    # --- TEMPERATURE: NORMAL (9 Kural) ---
    ctrl.Rule(temperature['normal'] & humidity['dry'] & room_size['small'], fan_speed['low']),
    ctrl.Rule(temperature['normal'] & humidity['dry'] & room_size['medium'], fan_speed['medium']),
    ctrl.Rule(temperature['normal'] & humidity['dry'] & room_size['large'], fan_speed['medium']),
    
    ctrl.Rule(temperature['normal'] & humidity['comfortable'] & room_size['small'], fan_speed['medium']),
    ctrl.Rule(temperature['normal'] & humidity['comfortable'] & room_size['medium'], fan_speed['medium']),
    ctrl.Rule(temperature['normal'] & humidity['comfortable'] & room_size['large'], fan_speed['high']),
    
    ctrl.Rule(temperature['normal'] & humidity['humid'] & room_size['small'], fan_speed['medium']),
    ctrl.Rule(temperature['normal'] & humidity['humid'] & room_size['medium'], fan_speed['high']),
    ctrl.Rule(temperature['normal'] & humidity['humid'] & room_size['large'], fan_speed['high']),

    # --- TEMPERATURE: HOT (9 Kural) ---
    ctrl.Rule(temperature['hot'] & humidity['dry'] & room_size['small'], fan_speed['medium']),
    ctrl.Rule(temperature['hot'] & humidity['dry'] & room_size['medium'], fan_speed['high']),
    ctrl.Rule(temperature['hot'] & humidity['dry'] & room_size['large'], fan_speed['high']),
    
    ctrl.Rule(temperature['hot'] & humidity['comfortable'] & room_size['small'], fan_speed['high']),
    ctrl.Rule(temperature['hot'] & humidity['comfortable'] & room_size['medium'], fan_speed['high']),
    ctrl.Rule(temperature['hot'] & humidity['comfortable'] & room_size['large'], fan_speed['high']),
    
    ctrl.Rule(temperature['hot'] & humidity['humid'] & room_size['small'], fan_speed['high']),
    ctrl.Rule(temperature['hot'] & humidity['humid'] & room_size['medium'], fan_speed['high']),
    ctrl.Rule(temperature['hot'] & humidity['humid'] & room_size['large'], fan_speed['high'])
]

system = ctrl.ControlSystem(rules)
sim = ctrl.ControlSystemSimulation(system)

# ----------------------------------------------------
# GİRDİLER (SIDEBAR SLIDERS) - (Arayüz)

st.sidebar.header("🎛️ Sensör Giriş Değerleri")

temp_val = st.sidebar.slider("Sıcaklık (Temperature) °C", 0.0, 50.0, 25.0, step=0.5)
humid_val = st.sidebar.slider("Nem Oranı (Humidity) %", 0.0, 100.0, 50.0, step=1.0)
room_val = st.sidebar.slider("Oda Boyutu (Room Size) m²", 5.0, 100.0, 30.0, step=1.0)

# ARAYÜZ İSTERİ 5: Hesapla Butonu Ekleme
calculate_btn = st.sidebar.button("⚙️ Fan Hızını Hesapla", type="primary")

# ----------------------------------------------------
# KONTROL SİSTEMİ ARAYÜZÜ

with tab_sistem:
    sim.input['temperature'] = temp_val
    sim.input['humidity'] = humid_val
    sim.input['room_size'] = room_val

    error_status = False
    try:
        sim.compute()
        result = sim.output['fan_speed']
    except Exception as e:
        result = 50.0
        error_status = True

    # Sonucu Sayısal Olarak Gösterme (Arayüz İsteri 4)
    st.subheader("🎯 Hesaplama Sonucu")
    if error_status:
        st.error(f"⚠️ Kritik Hesaplama Hatası! Güvenli çıktı atandı: %50.00")
    else:
        st.success(f"💡 Optimum Klima Fan Hızı: **% {result:.2f}**")

    st.metric("Hesaplanan Net Çıktı (Fan Hızı)", f"{result:.2f} %")
    st.divider()

    # Ekranı düzenli göstermek için iki ana sütuna bölüyoruz
    col_graphs, col_data = st.columns([1.2, 1])

    # ----------------------------------------------------
    # SOL SÜTUN: TÜM GRAFİKLER (Giriş ve Çıkış Grafikleri)
   
    with col_graphs:
        st.subheader("📈 Grafiksel Gösterimler")
        
        # 1. Giriş Kümelerinin Grafikleri (Arayüz İsteri 2)
        fig_inputs, axs = plt.subplots(3, 1, figsize=(10, 8))
        plt.subplots_adjust(hspace=0.6)
        
        # Sıcaklık Grafiği ve Anlık Durum Çizgisi
        axs[0].plot(temperature.universe, temperature['cold'].mf, 'b', label='Cold')
        axs[0].plot(temperature.universe, temperature['normal'].mf, 'g', label='Normal')
        axs[0].plot(temperature.universe, temperature['hot'].mf, 'r', label='Hot')
        axs[0].axvline(temp_val, color='purple', linewidth=2, linestyle='--', label=f'Mevcut: {temp_val}°C')
        axs[0].set_title("Sıcaklık Üyelik Fonksiyonları")
        axs[0].legend(loc='upper right')
        
        # Nem Grafiği ve Anlık Durum Çizgisi
        axs[1].plot(humidity.universe, humidity['dry'].mf, 'orange', label='Dry')
        axs[1].plot(humidity.universe, humidity['comfortable'].mf, 'g', label='Comfortable')
        axs[1].plot(humidity.universe, humidity['humid'].mf, 'b', label='Humid')
        axs[1].axvline(humid_val, color='purple', linewidth=2, linestyle='--', label=f'Mevcut: %{humid_val}')
        axs[1].set_title("Nem Üyelik Fonksiyonları")
        axs[1].legend(loc='upper right')
        
        # Oda Boyutu Grafiği ve Anlık Durum Çizgisi
        axs[2].plot(room_size.universe, room_size['small'].mf, 'b', label='Small')
        axs[2].plot(room_size.universe, room_size['medium'].mf, 'g', label='Medium')
        axs[2].plot(room_size.universe, room_size['large'].mf, 'r', label='Large')
        axs[2].axvline(room_val, color='purple', linewidth=2, linestyle='--', label=f'Mevcut: {room_val}m²')
        axs[2].set_title("Oda Boyutu Üyelik Fonksiyonları")
        axs[2].legend(loc='upper right')
        
        st.pyplot(fig_inputs, clear_figure=True)
        plt.close(fig_inputs)
        
        st.markdown("---")
        
        # 2. Çıkış Durulaştırma Grafiği (Arayüz İsteri 4)
        st.write("**Durulaştırma (Çıktı) Grafiği (Centroid):**")
        fig_out, ax_out = plt.subplots(figsize=(10, 3.5))
        x = fan_speed.universe
        ax_out.plot(x, fan_speed['low'].mf, 'b--', label="Low")
        ax_out.plot(x, fan_speed['medium'].mf, 'g--', label="Medium")
        ax_out.plot(x, fan_speed['high'].mf, 'r--', label="High")
        
        # Çıktı alan aktivasyonunu görsel olarak boyama
        try:
            low_act = np.fmin(sim.control_system.consequents[0].terms['low'].membership_value, fan_speed['low'].mf)
            med_act = np.fmin(sim.control_system.consequents[0].terms['medium'].membership_value, fan_speed['medium'].mf)
            high_act = np.fmin(sim.control_system.consequents[0].terms['high'].membership_value, fan_speed['high'].mf)
            aggregated = np.fmax(low_act, np.fmax(med_act, high_act))
            ax_out.fill_between(x, 0, aggregated, facecolor='Cyan', alpha=0.4, label="Aktivasyon Alanı")
        except:
            pass
            
        ax_out.axvline(result, color='red', linewidth=2.5, label=f'Centroid Çıktısı: {result:.2f}%')
        ax_out.set_title("Çıkış Kümesi ve Kesme Alanı")
        ax_out.legend(loc='upper left')
        
        st.pyplot(fig_out, clear_figure=True)
        plt.close(fig_out)

    # ----------------------------------------------------
    # SAĞ SÜTUN: BULANIKLAŞTIRMA VE AKTİF KURAL LİSTESİ
   
    with col_data:
        # 1. Tüm Girişlerin Üyelik Dereceleri (Arayüz İsteri 6)
        st.subheader("📊 Bulanıklaştırma Dereceleri")
        st.markdown("Girdilerin tüm dilsel terimlerdeki anlık üyelik değerleri ($\mu$):")
        
        t_cold = fuzz.interp_membership(temperature.universe, temperature['cold'].mf, temp_val)
        t_norm = fuzz.interp_membership(temperature.universe, temperature['normal'].mf, temp_val)
        t_hot = fuzz.interp_membership(temperature.universe, temperature['hot'].mf, temp_val)

        h_dry = fuzz.interp_membership(humidity.universe, humidity['dry'].mf, humid_val)
        h_conf = fuzz.interp_membership(humidity.universe, humidity['comfortable'].mf, humid_val)
        h_humid = fuzz.interp_membership(humidity.universe, humidity['humid'].mf, humid_val)

        r_small = fuzz.interp_membership(room_size.universe, room_size['small'].mf, room_val)
        r_med = fuzz.interp_membership(room_size.universe, room_size['medium'].mf, room_val)
        r_large = fuzz.interp_membership(room_size.universe, room_size['large'].mf, room_val)

        df_ui = pd.DataFrame({
            "Dilsel Seviye": ["Düşük / Soğuk / Kuru", "Orta / Normal / Konforlu", "Yüksek / Sıcak / Nemli"],
            "Sıcaklık (μ)": [t_cold, t_norm, t_hot],
            "Nem Oranı (μ)": [h_dry, h_conf, h_humid],
            "Oda Boyutu (μ)": [r_small, r_med, r_large]
        })
        st.dataframe(df_ui.style.format(precision=2), use_container_width=True)
        
        st.divider()
        
        # 2. Aktif Kural Listesi 
        st.subheader("📋 Aktif Kural Listesi")
        st.markdown("Şu an karara etki eden (`Aktivasyon Gücü > 0`) kurallar:")
        
        rule_check_list = [
            # Cold kombinasyonları
            ("Sıcaklık(COLD) AND Nem(DRY) AND Oda(SMALL) → Fan(LOW)", min(t_cold, h_dry, r_small)),
            ("Sıcaklık(COLD) AND Nem(DRY) AND Oda(MEDIUM) → Fan(LOW)", min(t_cold, h_dry, r_med)),
            ("Sıcaklık(COLD) AND Nem(DRY) AND Oda(LARGE) → Fan(MEDIUM)", min(t_cold, h_dry, r_large)),
            ("Sıcaklık(COLD) AND Nem(COMF) AND Oda(SMALL) → Fan(LOW)", min(t_cold, h_conf, r_small)),
            ("Sıcaklık(COLD) AND Nem(COMF) AND Oda(MEDIUM) → Fan(MEDIUM)", min(t_cold, h_conf, r_med)),
            ("Sıcaklık(COLD) AND Nem(COMF) AND Oda(LARGE) → Fan(MEDIUM)", min(t_cold, h_conf, r_large)),
            ("Sıcaklık(COLD) AND Nem(HUMID) AND Oda(SMALL) → Fan(MEDIUM)", min(t_cold, h_humid, r_small)),
            ("Sıcaklık(COLD) AND Nem(HUMID) AND Oda(MEDIUM) → Fan(MEDIUM)", min(t_cold, h_humid, r_med)),
            ("Sıcaklık(COLD) AND Nem(HUMID) AND Oda(LARGE) → Fan(HIGH)", min(t_cold, h_humid, r_large)),
            
            # Normal kombinasyonları
            ("Sıcaklık(NORMAL) AND Nem(DRY) AND Oda(SMALL) → Fan(LOW)", min(t_norm, h_dry, r_small)),
            ("Sıcaklık(NORMAL) AND Nem(DRY) AND Oda(MEDIUM) → Fan(MEDIUM)", min(t_norm, h_dry, r_med)),
            ("Sıcaklık(NORMAL) AND Nem(DRY) AND Oda(LARGE) → Fan(MEDIUM)", min(t_norm, h_dry, r_large)),
            ("Sıcaklık(NORMAL) AND Nem(COMF) AND Oda(SMALL) → Fan(MEDIUM)", min(t_norm, h_conf, r_small)),
            ("Sıcaklık(NORMAL) AND Nem(COMF) AND Oda(MEDIUM) → Fan(MEDIUM)", min(t_norm, h_conf, r_med)),
            ("Sıcaklık(NORMAL) AND Nem(COMF) AND Oda(LARGE) → Fan(HIGH)", min(t_norm, h_conf, r_large)),
            ("Sıcaklık(NORMAL) AND Nem(HUMID) AND Oda(SMALL) → Fan(MEDIUM)", min(t_norm, h_humid, r_small)),
            ("Sıcaklık(NORMAL) AND Nem(HUMID) AND Oda(MEDIUM) → Fan(HIGH)", min(t_norm, h_humid, r_med)),
            ("Sıcaklık(NORMAL) AND Nem(HUMID) AND Oda(LARGE) → Fan(HIGH)", min(t_norm, h_humid, r_large)),
            
            # Hot kombinasyonları
            ("Sıcaklık(HOT) AND Nem(DRY) AND Oda(SMALL) → Fan(MEDIUM)", min(t_hot, h_dry, r_small)),
            ("Sıcaklık(HOT) AND Nem(DRY) AND Oda(MEDIUM) → Fan(HIGH)", min(t_hot, h_dry, r_med)),
            ("Sıcaklık(HOT) AND Nem(DRY) AND Oda(LARGE) → Fan(HIGH)", min(t_hot, h_dry, r_large)),
            ("Sıcaklık(HOT) AND Nem(COMF) AND Oda(SMALL) → Fan(HIGH)", min(t_hot, h_conf, r_small)),
            ("Sıcaklık(HOT) AND Nem(COMF) AND Oda(MEDIUM) → Fan(HIGH)", min(t_hot, h_conf, r_med)),
            ("Sıcaklık(HOT) AND Nem(COMF) AND Oda(LARGE) → Fan(HIGH)", min(t_hot, h_conf, r_large)),
            ("Sıcaklık(HOT) AND Nem(HUMID) AND Oda(SMALL) → Fan(HIGH)", min(t_hot, h_humid, r_small)),
            ("Sıcaklık(HOT) AND Nem(HUMID) AND Oda(MEDIUM) → Fan(HIGH)", min(t_hot, h_humid, r_med)),
            ("Sıcaklık(HOT) AND Nem(HUMID) AND Oda(LARGE) → Fan(HIGH)", min(t_hot, h_humid, r_large))
        ]
        
        any_active = False
        for rule_str, strength in rule_check_list:
            if strength > 0:
                any_active = True
                st.info(f"**Aktif Kural:** IF {rule_str}  \n➡️ *Aktivasyon Gücü:* `{strength:.2f}`")
                
        if not any_active:
            st.warning("Hiçbir kural tetiklenemedi. Girişleri evrensel küme sınırlarına getirin.")

# ----------------------------------------------------
# 2. SEKME: RAPOR VE DEĞERLENDİRME METİNLERİ 

with tab_rapor:
    st.header("📝 Proje Raporu Dokümantasyonu")
    
    st.subheader("1. Problemin Tanımı ve Gerekçelendirme")
    st.markdown("""
    * **Gerçek Dünya Problemi:** Konvansiyonel klimalar, ortam sıcaklığına göre sadece 'Aç/Kapat' (On-Off) mantığıyla çalışır. Bu durum ani sıcaklık dalgalanmalarına, yüksek enerji tüketimine ve konforsuz bir iç mekana sebep olur.
    * **Giriş ve Çıkışlar:** Sistem; anlık **Sıcaklık**, **Nem** ve **Oda Boyutu** verilerini alarak optimum **Fan Hızı** çıktısını üretmektedir.
    * **Bulanık Mantığın Uygunluğu:** 'Sıcaklık 24 dereceyken klima dursun, 24.1 dereceyken tam güç çalışsın' gibi keskin (Crisp) kararlar insan konforuna terstir. İnsan algısındaki 'ılık', 'hafif nemli', 'geniş oda' gibi muğlak kavramlar matematiksel olarak en iyi **Bulanık Mantık (Fuzzy Logic)** ile modellenir. Sistem doğrusal olmayan (non-linear) bir karakter sergilediği için bu yöntem seçilmiştir.
    """)
    
    st.subheader("2. Test Senaryoları ve Analiz")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.markdown("**Senaryo 1: Aşırı Sıcak & Nemli (Büyük Salon)**")
        st.code("Giriş: 40°C, %85 Nem, 80m²\nBeklenen Çıktı: > %85 Fan Hızı\nYorum: Sistem ani soğutma için maksimum güce geçer.")
    with col_s2:
        st.markdown("**Senaryo 2: İdeal Kış Günü (Küçük Oda)**")
        st.code("Giriş: 16°C, %35 Nem, 12m²\nBeklenen Çıktı: < %25 Fan Hızı\nYorum: Hava zaten soğuk ve oda küçük olduğundan fan hızı minimuma çekilir.")
    with col_s3:
        st.markdown("**Senaryo 3: Ilıman Bahar Havası**")
        st.code("Giriş: 24°C, %55 Nem, 40m²\nBeklenen Çıktı: ~ %50 Fan Hızı\nYorum: Sistem konfor modunda orta düzeyde çalışır.")

    st.subheader("3. Güçlü/Zayıf Yönler & Güncel Yaklaşımlar")
    st.markdown("""
    * **Güçlü Yönler:** Matematiksel bir model transfer fonksiyonuna ihtiyaç duymaz. Tamamen uzman görüşü ve insan deneyimi (27 kural) ile tasarlanmıştır. Centroid yöntemi sayesinde kararlı ve pürüzsüz geçişler sunar.
    * **Zayıf Yönler:** Kural tabanı sabittir. Zamanla değişen dış ortam şartlarına veya binanın yalıtım kalitesine kendi kendine adapte olamaz (Öğrenme yeteneği yoktur).
    * **Güncel Yaklaşımlar ile Kıyaslama (ANFIS / Yapay Zirka):** Günümüzde salt bulanık mantık yerine, kuralları ve üyelik fonksiyonlarını veriden öğrenen **ANFIS (Fuzzy-Sinir Ağları Hibriti)** veya derin pekiştirmeli öğrenme (Reinforcement Learning) algoritmaları kullanılmaktadır. Bu projede tasarlanan sistem, otonom sistemlerin temel çekirdeğini oluşturmaktadır.
    """)