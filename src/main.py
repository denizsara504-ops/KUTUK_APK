"""
Kütük Sorgulama - Android / Kivy
SQLite tabanlı, tamamen offline çalışır
"""
import os
from pathlib import Path

# Android'de uygulama dizini
from kivy.utils import platform
if platform == 'android':
    from android.storage import primary_external_storage_path
    APP_DIR = Path(primary_external_storage_path()) / "KutukSorgulama"
else:
    APP_DIR = Path(__file__).parent.parent / "data"

APP_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = str(APP_DIR / "kutuk.db")

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from kivy.properties import StringProperty
import sqlite3

C_BLUE   = (0.20, 0.40, 0.70, 1)
C_GREEN  = (0.10, 0.55, 0.10, 1)
C_RED    = (0.75, 0.10, 0.10, 1)
C_ORANGE = (0.85, 0.40, 0.00, 1)
C_DARK   = (0.12, 0.12, 0.18, 1)
C_LIGHT  = (0.95, 0.95, 0.98, 1)
C_GRAY   = (0.45, 0.45, 0.50, 1)

KV = """
#:import dp kivy.metrics.dp
#:import C_BLUE   main.C_BLUE
#:import C_GREEN  main.C_GREEN
#:import C_RED    main.C_RED
#:import C_ORANGE main.C_ORANGE
#:import C_DARK   main.C_DARK
#:import C_LIGHT  main.C_LIGHT
#:import C_GRAY   main.C_GRAY

<RoundBtn@Button>:
    background_color: 0,0,0,0
    background_normal: ''
    canvas.before:
        Color:
            rgba: self.background_color if self.state=='normal' else [x*0.8 for x in self.background_color]
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(8)]

<ScreenManager>:
    SorgulamaEkrani:
        name: 'sorgulama'
    KayitDetayEkrani:
        name: 'detay'
    KayitFormEkrani:
        name: 'form'
    NotlarEkrani:
        name: 'notlar'
    AyarlarEkrani:
        name: 'ayarlar'

<SorgulamaEkrani>:
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: C_LIGHT
            Rectangle:
                pos: self.pos
                size: self.size

        # Başlık
        BoxLayout:
            size_hint_y: None
            height: dp(54)
            padding: dp(10), dp(6)
            spacing: dp(8)
            canvas.before:
                Color:
                    rgba: C_DARK
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                text: '[b]🔍  KÜTÜK SORGULAMA[/b]'
                markup: True
                color: 1,1,1,1
                font_size: dp(15)
                halign: 'left'
                text_size: self.size
                valign: 'middle'
            Button:
                text: '⚙'
                size_hint_x: None
                width: dp(44)
                font_size: dp(20)
                background_color: 0,0,0,0
                color: 1,1,1,1
                on_release: app.root.current = 'ayarlar'

        # Filtre alanları
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(210)
            padding: dp(8), dp(6)
            spacing: dp(4)
            canvas.before:
                Color:
                    rgba: 1,1,1,1
                Rectangle:
                    pos: self.pos
                    size: self.size

            BoxLayout:
                size_hint_y: None
                height: dp(44)
                spacing: dp(6)
                Label:
                    text: 'TC NO :'
                    size_hint_x: 0.30
                    halign: 'right'
                    text_size: self.size
                    valign: 'middle'
                    font_size: dp(13)
                    color: 0.3,0.3,0.5,1
                TextInput:
                    id: f_tc
                    hint_text: '11 haneli TC'
                    input_filter: 'int'
                    multiline: False
                    font_size: dp(14)
                    on_text_validate: root.sorgula()

            BoxLayout:
                size_hint_y: None
                height: dp(44)
                spacing: dp(6)
                Label:
                    text: 'ADI :'
                    size_hint_x: 0.30
                    halign: 'right'
                    text_size: self.size
                    valign: 'middle'
                    font_size: dp(13)
                    color: 0.3,0.3,0.5,1
                TextInput:
                    id: f_ad
                    hint_text: 'Adı'
                    multiline: False
                    font_size: dp(14)
                    on_text_validate: root.sorgula()

            BoxLayout:
                size_hint_y: None
                height: dp(44)
                spacing: dp(6)
                Label:
                    text: 'SOYADI :'
                    size_hint_x: 0.30
                    halign: 'right'
                    text_size: self.size
                    valign: 'middle'
                    font_size: dp(13)
                    color: 0.3,0.3,0.5,1
                TextInput:
                    id: f_soyad
                    hint_text: 'Soyadı'
                    multiline: False
                    font_size: dp(14)
                    on_text_validate: root.sorgula()

            BoxLayout:
                size_hint_y: None
                height: dp(44)
                spacing: dp(6)
                Label:
                    text: 'ANA ADI :'
                    size_hint_x: 0.30
                    halign: 'right'
                    text_size: self.size
                    valign: 'middle'
                    font_size: dp(13)
                    color: 0.3,0.3,0.5,1
                TextInput:
                    id: f_anaadi
                    hint_text: 'Ana adı'
                    multiline: False
                    font_size: dp(14)
                    on_text_validate: root.sorgula()

        # Butonlar
        BoxLayout:
            size_hint_y: None
            height: dp(48)
            padding: dp(8), dp(4)
            spacing: dp(8)
            canvas.before:
                Color:
                    rgba: 0.92,0.92,0.94,1
                Rectangle:
                    pos: self.pos
                    size: self.size
            RoundBtn:
                text: '[b]🔍  SORGULA[/b]'
                markup: True
                background_color: C_BLUE
                color: 1,1,1,1
                font_size: dp(14)
                on_release: root.sorgula()
            RoundBtn:
                text: '✖ SIFIRLA'
                background_color: C_ORANGE
                color: 1,1,1,1
                font_size: dp(13)
                size_hint_x: 0.38
                on_release: root.sifirla()

        # Sonuç sayısı
        Label:
            id: lbl_sonuc
            size_hint_y: None
            height: dp(26)
            text: 'Hazır — bir filtre girin'
            font_size: dp(12)
            color: C_GRAY
            halign: 'left'
            text_size: self.size
            padding: dp(10), 0

        # Sonuç listesi
        ScrollView:
            id: scroll_sonuc
            BoxLayout:
                id: liste_icerik
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height

        # Alt bar
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            padding: dp(8), dp(4)
            canvas.before:
                Color:
                    rgba: 0.88,0.88,0.92,1
                Rectangle:
                    pos: self.pos
                    size: self.size
            RoundBtn:
                text: '[b]➕  YENİ KAYIT[/b]'
                markup: True
                background_color: C_GREEN
                color: 1,1,1,1
                font_size: dp(14)
                on_release: root.yeni_kayit()

<KayitDetayEkrani>:
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: C_LIGHT
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            size_hint_y: None
            height: dp(54)
            padding: dp(8), dp(4)
            spacing: dp(6)
            canvas.before:
                Color:
                    rgba: C_DARK
                Rectangle:
                    pos: self.pos
                    size: self.size
            Button:
                text: '‹  Geri'
                size_hint_x: None
                width: dp(80)
                color: 1,1,1,1
                background_color: 0,0,0,0
                font_size: dp(14)
                on_release: app.root.current = 'sorgulama'
            Label:
                id: lbl_baslik
                text: 'Kayıt Detay'
                color: 1,1,1,1
                font_size: dp(14)
                bold: True

        ScrollView:
            BoxLayout:
                id: detay_icerik
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(10), dp(8)
                spacing: dp(2)

        BoxLayout:
            size_hint_y: None
            height: dp(54)
            padding: dp(8), dp(4)
            spacing: dp(6)
            canvas.before:
                Color:
                    rgba: 0.9,0.9,0.92,1
                Rectangle:
                    pos: self.pos
                    size: self.size
            RoundBtn:
                text: '[b]✏  DÜZENLE[/b]'
                markup: True
                background_color: C_BLUE
                color: 1,1,1,1
                font_size: dp(13)
                on_release: root.duzenle()
            RoundBtn:
                text: '📝  NOT'
                background_color: C_ORANGE
                color: 1,1,1,1
                font_size: dp(13)
                on_release: root.notlara_git()
            RoundBtn:
                text: '🗑  SİL'
                background_color: C_RED
                color: 1,1,1,1
                font_size: dp(13)
                on_release: root.sil_onayla()

<KayitFormEkrani>:
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: C_LIGHT
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            size_hint_y: None
            height: dp(54)
            padding: dp(8), dp(4)
            canvas.before:
                Color:
                    rgba: C_DARK
                Rectangle:
                    pos: self.pos
                    size: self.size
            Button:
                text: '‹  Geri'
                size_hint_x: None
                width: dp(80)
                color: 1,1,1,1
                background_color: 0,0,0,0
                font_size: dp(14)
                on_release: root.geri_don()
            Label:
                id: lbl_form_baslik
                text: 'Yeni Kayıt'
                color: 1,1,1,1
                font_size: dp(14)
                bold: True

        ScrollView:
            BoxLayout:
                id: form_alanlari
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(8), dp(6)
                spacing: dp(4)

        BoxLayout:
            size_hint_y: None
            height: dp(54)
            padding: dp(8), dp(4)
            canvas.before:
                Color:
                    rgba: 0.9,0.9,0.92,1
                Rectangle:
                    pos: self.pos
                    size: self.size
            RoundBtn:
                text: '[b]💾  KAYDET[/b]'
                markup: True
                background_color: C_GREEN
                color: 1,1,1,1
                font_size: dp(14)
                on_release: root.kaydet()

<NotlarEkrani>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: None
            height: dp(54)
            padding: dp(8), dp(4)
            canvas.before:
                Color:
                    rgba: C_DARK
                Rectangle:
                    pos: self.pos
                    size: self.size
            Button:
                text: '‹  Geri'
                size_hint_x: None
                width: dp(80)
                color: 1,1,1,1
                background_color: 0,0,0,0
                font_size: dp(14)
                on_release: app.root.current = 'detay'
            Label:
                text: '📝  Notlar'
                color: 1,1,1,1
                font_size: dp(14)
                bold: True
        TextInput:
            id: not_icerik
            hint_text: 'Notunuzu buraya yazın...'
            font_size: dp(14)
            multiline: True
        BoxLayout:
            size_hint_y: None
            height: dp(54)
            padding: dp(8), dp(4)
            canvas.before:
                Color:
                    rgba: 0.9,0.9,0.92,1
                Rectangle:
                    pos: self.pos
                    size: self.size
            RoundBtn:
                text: '[b]💾  NOTU KAYDET[/b]'
                markup: True
                background_color: C_GREEN
                color: 1,1,1,1
                font_size: dp(14)
                on_release: root.notu_kaydet()

<AyarlarEkrani>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: None
            height: dp(54)
            padding: dp(8), dp(4)
            canvas.before:
                Color:
                    rgba: C_DARK
                Rectangle:
                    pos: self.pos
                    size: self.size
            Button:
                text: '‹  Geri'
                size_hint_x: None
                width: dp(80)
                color: 1,1,1,1
                background_color: 0,0,0,0
                font_size: dp(14)
                on_release: app.root.current = 'sorgulama'
            Label:
                text: '⚙  Ayarlar'
                color: 1,1,1,1
                font_size: dp(14)
                bold: True
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(16)
                spacing: dp(14)

                Label:
                    text: '[b]📁  VERİTABANI KONUMU[/b]'
                    markup: True
                    size_hint_y: None
                    height: dp(34)
                    color: C_BLUE
                    halign: 'left'
                    text_size: self.size
                    font_size: dp(14)

                Label:
                    text: app.db_yolu_goster
                    size_hint_y: None
                    height: dp(60)
                    color: 0.3,0.3,0.3,1
                    halign: 'left'
                    text_size: self.size
                    font_size: dp(11)

                Label:
                    text: 'kutuk.db dosyasını USB ile bu konuma kopyalayın,\\nardından uygulamayı yeniden başlatın.'
                    size_hint_y: None
                    height: dp(50)
                    color: C_GRAY
                    halign: 'left'
                    text_size: self.size
                    font_size: dp(12)

                RoundBtn:
                    text: '🔄  Bağlantıyı Yenile'
                    background_color: C_BLUE
                    color: 1,1,1,1
                    size_hint_y: None
                    height: dp(46)
                    font_size: dp(14)
                    on_release: app.db_baglanti_kur()

                Label:
                    text: '[b]ℹ️  HAKKINDA[/b]'
                    markup: True
                    size_hint_y: None
                    height: dp(34)
                    color: C_BLUE
                    halign: 'left'
                    text_size: self.size
                    font_size: dp(14)

                Label:
                    text: 'Kütük Sorgulama v1.0\\nSQLite tabanlı — tamamen offline\\nSorgula · Ekle · Düzenle · Sil · Not'
                    size_hint_y: None
                    height: dp(70)
                    color: 0.4,0.4,0.4,1
                    halign: 'left'
                    text_size: self.size
                    font_size: dp(12)
"""

Builder.load_string(KV)


# ── EKRANLAR ──────────────────────────────────────────────────────────────────

class SorgulamaEkrani(Screen):

    def sorgula(self):
        tc     = self.ids.f_tc.text.strip()
        ad     = self.ids.f_ad.text.strip().upper()
        soyad  = self.ids.f_soyad.text.strip().upper()
        anaadi = self.ids.f_anaadi.text.strip().upper()

        app = App.get_running_app()
        sonuclar = app.db_ara(tc=tc, ad=ad, soyad=soyad, anaadi=anaadi)
        self.ids.lbl_sonuc.text = f"Bulunan sonuç: {len(sonuclar)}"
        self._listeyi_doldur(sonuclar)

    def _listeyi_doldur(self, sonuclar):
        liste = self.ids.liste_icerik
        liste.clear_widgets()
        for r in sonuclar[:300]:
            satir = self._satir_olustur(r)
            liste.add_widget(satir)

    def _satir_olustur(self, r):
        tc    = r.get('tc','')
        ad    = r.get('ad','')
        soyad = r.get('soyad','')
        dt    = r.get('dogumtarihi','')
        il    = r.get('nufusil','')

        kutu = BoxLayout(
            orientation='horizontal',
            size_hint_y=None, height=dp(70),
            padding=(dp(10), dp(6)), spacing=dp(8)
        )
        kutu.canvas.before.add  # Arka plan
        from kivy.graphics import Color, Rectangle, Line
        with kutu.canvas.before:
            Color(1, 1, 1, 1)
            kutu._bg = Rectangle(pos=kutu.pos, size=kutu.size)
            Color(0.82, 0.82, 0.86, 1)
            kutu._ln = Line(points=[kutu.x, kutu.y, kutu.x+kutu.width, kutu.y], width=1)
        kutu.bind(pos=lambda w,v: (setattr(w._bg,'pos',v), setattr(w._ln,'points',[v[0],v[1],v[0]+w.width,v[1]])),
                  size=lambda w,v: (setattr(w._bg,'size',v), setattr(w._ln,'points',[w.x,w.y,w.x+v[0],w.y])))

        bilgi = BoxLayout(orientation='vertical', spacing=dp(2))
        bilgi.add_widget(Label(
            text=f"[b]{ad} {soyad}[/b]", markup=True,
            font_size=dp(14), color=(0.1,0.1,0.15,1),
            halign='left', text_size=(dp(260), dp(22)), valign='middle'
        ))
        bilgi.add_widget(Label(
            text=f"TC: {tc}   DT: {dt}",
            font_size=dp(11), color=C_GRAY,
            halign='left', text_size=(dp(260), dp(18)), valign='middle'
        ))
        bilgi.add_widget(Label(
            text=il, font_size=dp(11), color=C_BLUE,
            halign='left', text_size=(dp(260), dp(18)), valign='middle'
        ))

        btn = Button(
            text='›', size_hint_x=None, width=dp(38),
            font_size=dp(22), color=C_BLUE,
            background_color=(0,0,0,0)
        )
        btn.bind(on_release=lambda _, t=tc: App.get_running_app().kayit_sec(t))

        kutu.add_widget(bilgi)
        kutu.add_widget(btn)
        return kutu

    def sifirla(self):
        for fld in ('f_tc','f_ad','f_soyad','f_anaadi'):
            self.ids[fld].text = ''
        self.ids.liste_icerik.clear_widgets()
        self.ids.lbl_sonuc.text = 'Hazır — bir filtre girin'

    def yeni_kayit(self):
        app = App.get_running_app()
        app.secili_tc = None
        self.manager.get_screen('form').formu_hazirla(None)
        self.manager.current = 'form'


class KayitDetayEkrani(Screen):

    def on_pre_enter(self):
        self._yukle()

    def _yukle(self):
        app = App.get_running_app()
        kayit = app.db_getir(app.secili_tc)
        if not kayit:
            return
        self.ids.lbl_baslik.text = f"{kayit.get('ad','')} {kayit.get('soyad','')}"
        ic = self.ids.detay_icerik
        ic.clear_widgets()
        ALANLAR = [
            ("TC NO",         'tc'),
            ("ADI",           'ad'),
            ("SOYADI",        'soyad'),
            ("ANA ADI",       'anaadi'),
            ("BABA ADI",      'babaadi'),
            ("DOĞUM YERİ",    'dogumyeri'),
            ("DOĞUM TARİHİ", 'dogumtarihi'),
            ("CİNSİYET",      'cinsiyet'),
            ("NÜFUS İLİ",    'nufusil'),
            ("NÜFUS İLÇESİ", 'nufusilce'),
            ("ADRES İLİ",    'adresil'),
            ("ADRES İLÇESİ", 'adresilce'),
            ("MAHALLE",       'mahalle'),
            ("CADDE/SOKAK",   'cadde'),
            ("KAPI NO",       'kapino'),
            ("DAİRE NO",      'daireno'),
        ]
        for etiket, alan in ALANLAR:
            deger = str(kayit.get(alan, '') or '')
            satir = BoxLayout(
                orientation='horizontal',
                size_hint_y=None, height=dp(38), spacing=dp(8)
            )
            satir.add_widget(Label(
                text=f"[b]{etiket}[/b]", markup=True,
                size_hint_x=0.38, halign='right', valign='middle',
                text_size=(dp(130), dp(38)), font_size=dp(12),
                color=(0.3,0.3,0.5,1)
            ))
            satir.add_widget(Label(
                text=deger, size_hint_x=0.62,
                halign='left', valign='middle',
                text_size=(dp(210), dp(38)), font_size=dp(13),
                color=(0.1,0.1,0.1,1)
            ))
            ic.add_widget(satir)

        not_metni = app.db_not_getir(app.secili_tc)
        if not_metni:
            ic.add_widget(Label(
                text="[b]📝  NOT[/b]", markup=True,
                size_hint_y=None, height=dp(30),
                halign='left', text_size=(dp(350), dp(30)),
                color=C_ORANGE, font_size=dp(13)
            ))
            ic.add_widget(Label(
                text=not_metni,
                size_hint_y=None, height=dp(max(50, not_metni.count('\n')*20+40)),
                halign='left', valign='top',
                text_size=(dp(350), None), font_size=dp(13),
                color=(0.2,0.2,0.2,1)
            ))

    def duzenle(self):
        app = App.get_running_app()
        kayit = app.db_getir(app.secili_tc)
        self.manager.get_screen('form').formu_hazirla(kayit)
        self.manager.current = 'form'

    def notlara_git(self):
        app = App.get_running_app()
        not_ekrani = self.manager.get_screen('notlar')
        not_ekrani.ids.not_icerik.text = app.db_not_getir(app.secili_tc) or ''
        self.manager.current = 'notlar'

    def sil_onayla(self):
        ic = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(10))
        ic.add_widget(Label(
            text='Bu kaydı kalıcı olarak\nsilmek istiyor musunuz?',
            halign='center', font_size=dp(14), color=(0.1,0.1,0.1,1)
        ))
        btns = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        popup = Popup(title='Kaydı Sil', content=ic, size_hint=(0.85,0.35))

        def sil(_):
            App.get_running_app().db_sil(App.get_running_app().secili_tc)
            popup.dismiss()
            self.manager.current = 'sorgulama'
            self.manager.get_screen('sorgulama').sifirla()

        btn_sil = Button(text='SİL', background_color=(0.75,0.1,0.1,1), color=(1,1,1,1))
        btn_iptal = Button(text='İptal', background_color=C_GRAY, color=(1,1,1,1))
        btn_sil.bind(on_release=sil)
        btn_iptal.bind(on_release=popup.dismiss)
        btns.add_widget(btn_sil)
        btns.add_widget(btn_iptal)
        ic.add_widget(btns)
        popup.open()


class KayitFormEkrani(Screen):
    _inputs = {}
    _duzenle_tc = None

    ALANLAR = [
        ("TC NO *",        'tc',          'int',  True),
        ("ADI *",          'ad',          'text', True),
        ("SOYADI *",       'soyad',       'text', True),
        ("ANA ADI",        'anaadi',      'text', False),
        ("BABA ADI",       'babaadi',     'text', False),
        ("DOĞUM YERİ",     'dogumyeri',   'text', False),
        ("DOĞUM TARİHİ",  'dogumtarihi', 'text', False),
        ("CİNSİYET",       'cinsiyet',    'spin', False),
        ("NÜFUS İLİ",     'nufusil',     'text', False),
        ("NÜFUS İLÇESİ",  'nufusilce',   'text', False),
        ("ADRES İLİ",     'adresil',     'text', False),
        ("ADRES İLÇESİ",  'adresilce',   'text', False),
        ("MAHALLE",        'mahalle',     'text', False),
        ("CADDE/SOKAK",    'cadde',       'text', False),
        ("KAPI NO",        'kapino',      'text', False),
        ("DAİRE NO",       'daireno',     'text', False),
    ]

    def formu_hazirla(self, kayit):
        self._inputs = {}
        self._duzenle_tc = kayit.get('tc') if kayit else None
        self.ids.lbl_form_baslik.text = 'Kayıt Düzenle' if kayit else 'Yeni Kayıt'
        form = self.ids.form_alanlari
        form.clear_widgets()
        for etiket, alan, tip, zorunlu in self.ALANLAR:
            satir = BoxLayout(
                orientation='horizontal',
                size_hint_y=None, height=dp(50),
                spacing=dp(6), padding=(dp(2), dp(2))
            )
            satir.add_widget(Label(
                text=etiket, size_hint_x=0.34,
                halign='right', valign='middle',
                text_size=(dp(115), dp(50)), font_size=dp(12),
                color=(0.3,0.3,0.5,1)
            ))
            mevcut = str(kayit.get(alan,'') or '') if kayit else ''
            if tip == 'spin':
                inp = Spinner(values=['E','K',''], text=mevcut, font_size=dp(14))
            else:
                inp = TextInput(
                    text=mevcut, multiline=False, font_size=dp(14),
                    input_filter='int' if tip=='int' else None,
                    hint_text='Zorunlu' if zorunlu else ''
                )
            self._inputs[alan] = inp
            satir.add_widget(inp)
            form.add_widget(satir)

    def kaydet(self):
        d = {k: (w.text.strip().upper() if k != 'tc' else w.text.strip())
             for k, w in self._inputs.items()}
        if not d.get('tc') or not d.get('ad') or not d.get('soyad'):
            self._hata('TC No, Ad ve Soyad zorunludur!'); return
        if len(d['tc']) != 11:
            self._hata('TC numarası 11 haneli olmalıdır!'); return
        app = App.get_running_app()
        if self._duzenle_tc:
            app.db_guncelle(self._duzenle_tc, d)
            app.secili_tc = d['tc']
            self.manager.current = 'detay'
        else:
            if app.db_ekle(d):
                app.secili_tc = d['tc']
                self.manager.current = 'detay'
            else:
                self._hata('Bu TC zaten kayıtlı!')

    def _hata(self, msg):
        Popup(title='Hata',
              content=Label(text=msg, halign='center', font_size=dp(14)),
              size_hint=(0.82, 0.25)).open()

    def geri_don(self):
        app = App.get_running_app()
        self.manager.current = 'detay' if app.secili_tc else 'sorgulama'


class NotlarEkrani(Screen):
    def notu_kaydet(self):
        app = App.get_running_app()
        app.db_not_kaydet(app.secili_tc, self.ids.not_icerik.text.strip())
        self.manager.current = 'detay'


class AyarlarEkrani(Screen):
    pass


# ── ANA UYGULAMA ──────────────────────────────────────────────────────────────

class KutukApp(App):
    db_yolu_goster = StringProperty(DB_PATH)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.secili_tc = None
        self._conn = None

    def build(self):
        self.title = 'Kütük Sorgulama'
        self.db_baglanti_kur()
        sm = ScreenManager(transition=SlideTransition())
        return sm

    def db_baglanti_kur(self, *_):
        try:
            if self._conn:
                try: self._conn.close()
                except: pass
            self._conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=NORMAL")
            self._conn.execute("PRAGMA cache_size=80000")   # ~320 MB cache
            self._conn.execute("PRAGMA temp_store=memory")
            self._conn.execute("PRAGMA mmap_size=1073741824")  # 1 GB mmap
            self._init_tablolar()
            self.db_yolu_goster = DB_PATH
        except Exception as e:
            print(f"DB hatası: {e}")

    def _init_tablolar(self):
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS secmen (
                tc TEXT PRIMARY KEY,
                ad TEXT, soyad TEXT, anaadi TEXT, babaadi TEXT,
                dogumyeri TEXT, dogumtarihi TEXT, cinsiyet TEXT,
                nufusil TEXT, nufusilce TEXT, adresil TEXT, adresilce TEXT,
                mahalle TEXT, cadde TEXT, kapino TEXT, daireno TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_ad_soyad  ON secmen(ad, soyad);
            CREATE INDEX IF NOT EXISTS idx_soyad     ON secmen(soyad);
            CREATE INDEX IF NOT EXISTS idx_nufusil   ON secmen(nufusil, nufusilce);
            CREATE INDEX IF NOT EXISTS idx_adresil   ON secmen(adresil, adresilce);
            CREATE TABLE IF NOT EXISTS notlar (
                tc TEXT PRIMARY KEY,
                metin TEXT,
                tarih TEXT DEFAULT (datetime('now'))
            );
        """)
        self._conn.commit()

    # ── DB İşlemleri ──────────────────────────────────────────────────────────

    def db_ara(self, tc='', ad='', soyad='', anaadi=''):
        if not self._conn: return []
        try:
            kosullar, params = [], []
            if tc:
                kosullar.append("tc=?");              params.append(tc)
            if ad:
                kosullar.append("ad LIKE ?");         params.append(ad+'%')
            if soyad:
                kosullar.append("soyad LIKE ?");      params.append(soyad+'%')
            if anaadi:
                kosullar.append("anaadi LIKE ?");     params.append(anaadi+'%')
            if not kosullar: return []
            where = " AND ".join(kosullar)
            cur = self._conn.execute(
                f"SELECT tc,ad,soyad,dogumtarihi,nufusil FROM secmen WHERE {where} LIMIT 300",
                params)
            return [dict(r) for r in cur.fetchall()]
        except Exception as e:
            print(f"Arama: {e}"); return []

    def db_getir(self, tc):
        if not self._conn or not tc: return None
        try:
            cur = self._conn.execute("SELECT * FROM secmen WHERE tc=?", (tc,))
            r = cur.fetchone()
            return dict(r) if r else None
        except Exception as e:
            print(f"Getir: {e}"); return None

    def db_ekle(self, d):
        try:
            self._conn.execute("""
                INSERT INTO secmen VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, tuple(d.get(k,'') for k in [
                'tc','ad','soyad','anaadi','babaadi','dogumyeri','dogumtarihi',
                'cinsiyet','nufusil','nufusilce','adresil','adresilce',
                'mahalle','cadde','kapino','daireno'
            ]))
            self._conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Ekle: {e}"); return False

    def db_guncelle(self, eski_tc, d):
        try:
            self._conn.execute("""
                UPDATE secmen SET tc=?,ad=?,soyad=?,anaadi=?,babaadi=?,
                dogumyeri=?,dogumtarihi=?,cinsiyet=?,nufusil=?,nufusilce=?,
                adresil=?,adresilce=?,mahalle=?,cadde=?,kapino=?,daireno=?
                WHERE tc=?
            """, tuple(d.get(k,'') for k in [
                'tc','ad','soyad','anaadi','babaadi','dogumyeri','dogumtarihi',
                'cinsiyet','nufusil','nufusilce','adresil','adresilce',
                'mahalle','cadde','kapino','daireno'
            ]) + (eski_tc,))
            self._conn.commit()
        except Exception as e:
            print(f"Güncelle: {e}")

    def db_sil(self, tc):
        try:
            self._conn.execute("DELETE FROM secmen WHERE tc=?", (tc,))
            self._conn.execute("DELETE FROM notlar WHERE tc=?", (tc,))
            self._conn.commit()
        except Exception as e:
            print(f"Sil: {e}")

    def db_not_getir(self, tc):
        try:
            cur = self._conn.execute("SELECT metin FROM notlar WHERE tc=?", (tc,))
            r = cur.fetchone()
            return r[0] if r else ''
        except: return ''

    def db_not_kaydet(self, tc, metin):
        try:
            self._conn.execute("""
                INSERT INTO notlar(tc,metin) VALUES(?,?)
                ON CONFLICT(tc) DO UPDATE SET metin=excluded.metin, tarih=datetime('now')
            """, (tc, metin))
            self._conn.commit()
        except Exception as e:
            print(f"Not kaydet: {e}")

    def kayit_sec(self, tc):
        self.secili_tc = tc
        self.root.current = 'detay'

    def on_stop(self):
        if self._conn:
            try: self._conn.close()
            except: pass


if __name__ == '__main__':
    KutukApp().run()
