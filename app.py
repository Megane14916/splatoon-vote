import os
import itertools
import math
from flask import Flask, render_template, request, jsonify
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_sqlalchemy import SQLAlchemy # SQLAlchemyをインポート

app = Flask(__name__)

# --- セキュリティと基本設定 ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-very-secret-string-that-you-should-change')
csrf = CSRFProtect(app)

# --- データベース設定 (PostgreSQL) ---
# Vercelの環境変数からデータベースURLを取得。なければローカルのSQLiteをフォールバックとして設定（開発用）
db_url = os.environ.get('POSTGRES_URL')
if db_url:
    # Vercel PostgresのURLは "postgres://" で始まるので "postgresql://" に置換する必要がある
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
else:
    # ローカル開発用のフォールバック
    db_url = "sqlite:///splat_votes.db"

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- レートリミット設定 (変更なし) ---
def get_real_ip():
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    return request.remote_addr
limiter = Limiter(key_func=get_real_ip, app=app)


# --- データベースモデル定義 ---
class Votes(db.Model):
    __tablename__ = 'votes'
    weapon_id = db.Column(db.Integer, primary_key=True)
    vote_count = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f'<Vote {self.weapon_id}>'

# --- 武器データの定義 (変更なし) ---
main_weapons_list = [
    {"name": "わかばシューター", "type": "シューター", "image": "Splattershot_Jr.png"},
    {"name": "ボールドマーカー", "type": "シューター", "image": "Sploosh-o-matic.png"},
    {"name": "シャープマーカー", "type": "シューター", "image": "Splash-o-matic.png"},
    {"name": "プロモデラー", "type": "シューター", "image": "Aerospray.png"},
    {"name": "スプラシューター", "type": "シューター", "image": "Splattershot.png"},
    {"name": ".52ガロン", "type": "シューター", "image": ".52_Gal.png"},
    {"name": "N-ZAP", "type": "シューター", "image": "N-ZAP.png"},
    {"name": "プライムシューター", "type": "シューター", "image": "Splattershot_Pro.png"},
    {"name": ".96ガロン", "type": "シューター", "image": ".96_Gal.png"},
    {"name": "ジェットスイーパー", "type": "シューター", "image": "Jet_Squelcher.png"},
    {"name": "L3リールガン", "type": "シューター", "image": "L-3_Nozzlenose.png"},
    {"name": "H3リールガン", "type": "シューター", "image": "H-3_Nozzlenose.png"},
    {"name": "ボトルガイザー", "type": "シューター", "image": "Squeezer.png"},
    {"name": "スペースシューター", "type": "シューター", "image": "Splattershot_Nova.png"},
    
    {"name": "カーボンローラー", "type": "ローラー", "image": "Carbon_Roller.png"},
    {"name": "スプラローラー", "type": "ローラー", "image": "Splat_Roller.png"},
    {"name": "ダイナモローラー", "type": "ローラー", "image": "Dynamo_Roller.png"},
    {"name": "ヴァリアブルローラー", "type": "ローラー", "image": "Flingza_Roller.png"},
    {"name": "ワイドローラー", "type": "ローラー", "image": "Big_Swig_Roller.png"},

    {"name": "スクイックリン", "type": "チャージャー", "image": "Classic_Squiffer.png"},
    {"name": "スプラチャージャー", "type": "チャージャー", "image": "Splat_Charger.png"},
    {"name": "スプラスコープ", "type": "チャージャー", "image": "Splatterscope.png"},
    {"name": "リッター4K", "type": "チャージャー", "image": "E-liter_4K.png"},
    {"name": "4Kスコープ", "type": "チャージャー", "image": "E-liter_4K_Scope.png"},
    {"name": "14式竹筒銃", "type": "チャージャー", "image": "Bamboozler_14.png"},
    {"name": "ソイチューバー", "type": "チャージャー", "image": "Goo_Tuber.png"},
    {"name": "R-PEN", "type": "チャージャー", "image": "Snipewriter.png"},

    {"name": "ヒッセン", "type": "スロッシャー", "image": "Tri-Slosher.png"},
    {"name": "バケットスロッシャー", "type": "スロッシャー", "image": "Slosher.png"},
    {"name": "スクリュースロッシャー", "type": "スロッシャー", "image": "Sloshing_Machine.png"},
    {"name": "オーバーフロッシャー", "type": "スロッシャー", "image": "Bloblobber.png"},
    {"name": "エクスプロッシャー", "type": "スロッシャー", "image": "Explosher.png"},
    {"name": "モップリン", "type": "スロッシャー", "image": "Dread_Wringer.png"},

    {"name": "スプラスピナー", "type": "スピナー", "image": "Mini_Splatling.png"},
    {"name": "バレルスピナー", "type": "スピナー", "image": "Heavy_Splatling.png"},
    {"name": "ハイドラント", "type": "スピナー", "image": "Hydra_Splatling.png"},
    {"name": "クーゲルシュライバー", "type": "スピナー", "image": "Ballpoint_Splatling.png"},
    {"name": "ノーチラス", "type": "スピナー", "image": "Nautilus.png"},
    {"name": "イグザミナー", "type": "スピナー", "image": "Heavy_Edit_Splatling.png"},

    {"name": "スパッタリー", "type": "マニューバー", "image": "Dapple_Dualies.png"},
    {"name": "スプラマニューバー", "type": "マニューバー", "image": "Splat_Dualies.png"},
    {"name": "デュアルスイーパー", "type": "マニューバー", "image": "Dualie_Squelchers.png"},
    {"name": "ケルビン525", "type": "マニューバー", "image": "Glooga_Dualies.png"},
    {"name": "クアッドホッパー", "type": "マニューバー", "image": "Tetra_Dualies.png"},
    {"name": "ガエンFF", "type": "マニューバー", "image": "Douser_Dualies_FF.png"},

    {"name": "パラシェルター", "type": "シェルター", "image": "Splat_Brella.png"},
    {"name": "キャンピングシェルター", "type": "シェルター", "image": "Tenta_Brella.png"},
    {"name": "スパイガジェット", "type": "シェルター", "image": "Undercover_Brella.png"},
    {"name": "24式張替傘", "type": "シェルター", "image": "Recycled_Brella.png"},
    
    {"name": "ノヴァブラスター", "type": "ブラスター", "image": "Luna_Blaster.png"},
    {"name": "ホットブラスター", "type": "ブラスター", "image": "Blaster.png"},
    {"name": "ロングブラスター", "type": "ブラスター", "image": "Range_Blaster.png"},
    {"name": "ラピッドブラスター", "type": "ブラスター", "image": "Rapid_Blaster.png"},
    {"name": "Rブラスターエリート", "type": "ブラスター", "image": "Rapid_Blaster_Pro.png"},
    {"name": "クラッシュブラスター", "type": "ブラスター", "image": "Clash_Blaster.png"},
    {"name": "S-BLAST", "type": "ブラスター", "image": "S-BLAST.png"},
    
    {"name": "パブロ", "type": "フデ", "image": "Inkbrush.png"},
    {"name": "ホクサイ", "type": "フデ", "image": "Octobrush.png"},
    {"name": "フィンセント", "type": "フデ", "image": "Painbrush.png"},
    
    {"name": "トライストリンガー", "type": "ストリンガー", "image": "Tri-Stringer.png"},
    {"name": "LACT-450", "type": "ストリンガー", "image": "REEF-LUX_450.png"},
    {"name": "フルイドV", "type": "ストリンガー", "image": "Wellstring_V.png"},

    {"name": "ドライブワイパー", "type": "ワイパー", "image": "Splatana_Wiper.png"},
    {"name": "ジムワイパー", "type": "ワイパー", "image": "Splatana_Stamper.png"},
    {"name": "デンタルワイパー", "type": "ワイパー", "image": "Mint_Decavitator.png"}
]
sub_weapons_list = [
    {"name": "スプラッシュボム", "image": "Splat_Bomb.png"},
    {"name": "キューバンボム", "image": "Suction_Bomb.png"},
    {"name": "クイックボム", "image": "Burst_Bomb.png"},
    {"name": "スプリンクラー", "image": "Sprinkler.png"},
    {"name": "スプラッシュシールド", "image": "Splash_Wall.png"},
    {"name": "タンサンボム", "image": "Fizzy_Bomb.png"},
    {"name": "カーリングボム", "image": "Curling_Bomb.png"},
    {"name": "ロボットボム", "image": "Autobomb.png"},
    {"name": "ジャンプビーコン", "image": "Squid_Beakon.png"},
    {"name": "ポイントセンサー", "image": "Point_Sensor.png"},
    {"name": "トラップ", "image": "Ink_Mine.png"},
    {"name": "ポイズンミスト", "image": "Toxic_Mist.png"},
    {"name": "ラインマーカー", "image": "Angle_Shooter.png"},
    {"name": "トーピード", "image": "Torpedo.png"}
]
special_weapons_list = [
    {"name": "ウルトラショット", "image": "Trizooka.png"},
    {"name": "グレートバリア", "image": "Big_Bubbler.png"},
    {"name": "ショクワンダー", "image": "Zipcaster.png"},
    {"name": "マルチミサイル", "image": "Tenta_Missiles.png"},
    {"name": "アメフラシ", "image": "Ink_Storm.png"},
    {"name": "ナイスダマ", "image": "Booyah_Bomb.png"},
    {"name": "ホップソナー", "image": "Wave_Breaker.png"},
    {"name": "キューインキ", "image": "Ink_Vac.png"},
    {"name": "メガホンレーザー5.1ch", "image": "Killer_Wail_5.1.png"},
    {"name": "ジェットパック", "image": "Inkjet.png"},
    {"name": "ウルトラハンコ", "image": "Ultra_Stamp.png"},
    {"name": "カニタンク", "image": "Crab_Tank.png"},
    {"name": "サメライド", "image": "Reefslider.png"},
    {"name": "トリプルトルネード", "image": "Triple_Inkstrike.png"},
    {"name": "エナジースタンド", "image": "Tacticooler.png"},
    {"name": "テイオウイカ", "image": "Kraken_Royale.png"},
    {"name": "デコイチラシ", "image": "Super_Chump.png"},
    {"name": "スミナガシート", "image": "Ink_Storm.png"},
    {"name": "ウルトラチャクチ", "image": "Triple_Splashdown.png"}
]

excluded_kits = [
    # シューター
    ("わかばシューター", "スプラッシュボム", "グレートバリア"),
    ("わかばシューター", "トーピード", "ホップソナー"),
    ("スプラシューター", "キューバンボム", "ウルトラショット"),
    ("スプラシューター", "スプラッシュボム", "トリプルトルネード"),
    ("スプラシューター", "クイックボム", "テイオウイカ"),
    ("シャープマーカー", "クイックボム", "カニタンク"),
    ("シャープマーカー", "キューバンボム", "トリプルトルネード"),
    ("シャープマーカー", "ポイズンミスト", "アメフラシ"),
    ("プロモデラー", "タンサンボム", "サメライド"),
    ("プロモデラー", "スプリンクラー", "ナイスダマ"),
    ("プロモデラー", "クイックボム", "スミナガシート"),
    ("ボールドマーカー", "カーリングボム", "ウルトラハンコ"),
    ("ボールドマーカー", "ジャンプビーコン", "メガホンレーザー5.1ch"),
    (".52ガロン", "スプラッシュシールド", "メガホンレーザー5.1ch"),
    (".52ガロン", "カーリングボム", "スミナガシート"),
    ("N-ZAP", "キューバンボム", "エナジースタンド"),
    ("N-ZAP", "ロボットボム", "デコイチラシ"),
    ("プライムシューター", "ラインマーカー", "カニタンク"),
    ("プライムシューター", "キューバンボム", "ナイスダマ"),
    ("プライムシューター", "スプラッシュボム", "マルチミサイル"),
    (".96ガロン", "スプリンクラー", "キューインキ"),
    (".96ガロン", "スプラッシュシールド", "テイオウイカ"),
    (".96ガロン", "ラインマーカー", "エナジースタンド"),
    ("ジェットスイーパー", "ラインマーカー", "キューインキ"),
    ("ジェットスイーパー", "ポイズンミスト", "アメフラシ"),
    ("ジェットスイーパー", "クイックボム", "ウルトラチャクチ"),
    ("スペースシューター", "ポイントセンサー", "メガホンレーザー5.1ch"),
    ("スペースシューター", "トラップ", "ジェットパック"),
    ("L3リールガン", "カーリングボム", "カニタンク"),
    ("L3リールガン", "クイックボム", "ウルトラハンコ"),
    ("L3リールガン", "スプラッシュボム", "ジェットパック"),
    ("H3リールガン", "ポイントセンサー", "エナジースタンド"),
    ("H3リールガン", "スプラッシュシールド", "グレートバリア"),
    ("H3リールガン", "キューバンボム", "トリプルトルネード"),
    ("ボトルガイザー", "スプラッシュシールド", "ウルトラショット"),
    ("ボトルガイザー", "ロボットボム", "スミナガシート"),

    # ブラスター
    ("ホットブラスター", "ロボットボム", "グレートバリア"),
    ("ホットブラスター", "ポイントセンサー", "ウルトラチャクチ"),
    ("ホットブラスター", "ジャンプビーコン", "カニタンク"),
    ("ロングブラスター", "キューバンボム", "ホップソナー"),
    ("ラピッドブラスター", "トラップ", "トリプルトルネード"),
    ("ラピッドブラスター", "トーピード", "ジェットパック"),
    ("クラッシュブラスター", "スプラッシュボム", "ウルトラショット"),
    ("クラッシュブラスター", "カーリングボム", "デコイチラシ"),
    ("ノヴァブラスター", "スプラッシュボム", "ショクワンダー"),
    ("ノヴァブラスター", "タンサンボム", "ウルトラハンコ"),
    ("Rブラスターエリート", "ポイズンミスト", "キューインキ"),
    ("Rブラスターエリート", "ラインマーカー", "メガホンレーザー5.1ch"),
    ("Rブラスターエリート", "キューバンボム", "エナジースタンド"),
    ("S-BLAST", "クイックボム", "ナイスダマ"),
    ("S-BLAST", "スプリンクラー", "サメライド"),

    # ローラー
    ("スプラローラー", "カーリングボム", "グレートバリア"),
    ("スプラローラー", "ジャンプビーコン", "テイオウイカ"),
    ("カーボンローラー", "ロボットボム", "ショクワンダー"),
    ("カーボンローラー", "クイックボム", "ウルトラショット"),
    ("カーボンローラー", "タンサンボム", "デコイチラシ"),
    ("ダイナモローラー", "スプリンクラー", "エナジースタンド"),
    ("ダイナモローラー", "スプラッシュボム", "デコイチラシ"),
    ("ヴァリアブルローラー", "トラップ", "マルチミサイル"),
    ("ヴァリアブルローラー", "キューバンボム", "スミナガシート"),
    ("ワイドローラー", "スプラッシュシールド", "キューインキ"),
    ("ワイドローラー", "ラインマーカー", "アメフラシ"),
    ("ワイドローラー", "トーピード", "ウルトラチャクチ"),

    # フデ
    ("パブロ", "スプラッシュボム", "メガホンレーザー5.1ch"),
    ("パブロ", "トラップ", "ウルトラハンコ"),
    ("ホクサイ", "キューバンボム", "ショクワンダー"),
    ("ホクサイ", "ジャンプビーコン", "アメフラシ"),
    ("ホクサイ", "ロボットボム", "テイオウイカ"),
    ("フィンセント", "カーリングボム", "ホップソナー"),
    ("フィンセント", "ポイントセンサー", "マルチミサイル"),
    ("フィンセント", "スプラッシュシールド", "ウルトラショット"),

    # チャージャー
    ("スプラチャージャー", "スプラッシュボム", "キューインキ"),
    ("スプラチャージャー", "スプリンクラー", "カニタンク"),
    ("スプラスコープ", "スプラッシュボム", "キューインキ"),
    ("スプラチャージャー", "スプラッシュシールド", "トリプルトルネード"),
    ("スプラスコープ", "スプラッシュシールド", "トリプルトルネード"),
    ("スプラスコープ", "スプリンクラー", "カニタンク"),
    ("リッター4K", "トラップ", "ホップソナー"),
    ("4Kスコープ", "トラップ", "ホップソナー"),
    ("リッター4K", "ジャンプビーコン", "テイオウイカ"),
    ("4Kスコープ", "ジャンプビーコン", "テイオウイカ"),
    ("14式竹筒銃", "ロボットボム", "メガホンレーザー5.1ch"),
    ("14式竹筒銃", "タンサンボム", "デコイチラシ"),
    ("ソイチューバー", "トーピード", "マルチミサイル"),
    ("ソイチューバー", "タンサンボム", "ウルトラハンコ"),
    ("スクイックリン", "ポイントセンサー", "グレートバリア"),
    ("スクイックリン", "ロボットボム", "ショクワンダー"),
    ("R-PEN", "スプリンクラー", "エナジースタンド"),
    ("R-PEN", "スプラッシュシールド", "アメフラシ"),

    # スロッシャー
    ("バケットスロッシャー", "スプラッシュボム", "トリプルトルネード"),
    ("バケットスロッシャー", "ラインマーカー", "ショクワンダー"),
    ("ヒッセン", "ポイズンミスト", "ジェットパック"),
    ("ヒッセン", "タンサンボム", "エナジースタンド"),
    ("ヒッセン", "スプラッシュボム", "スミナガシート"),
    ("スクリュースロッシャー", "タンサンボム", "ナイスダマ"),
    ("スクリュースロッシャー", "ポイントセンサー", "ウルトラショット"),
    ("オーバーフロッシャー", "スプリンクラー", "アメフラシ"),
    ("オーバーフロッシャー", "ラインマーカー", "テイオウイカ"),
    ("エクスプロッシャー", "ポイントセンサー", "アメフラシ"),
    ("エクスプロッシャー", "スプラッシュシールド", "ウルトラチャクチ"),
    ("モップリン", "キューバンボム", "サメライド"),
    ("モップリン", "ジャンプビーコン", "ホップソナー"),
    ("モップリン", "カーリングボム", "カニタンク"),

    # スピナー
    ("スプラスピナー", "クイックボム", "ウルトラハンコ"),
    ("スプラスピナー", "ポイズンミスト", "グレートバリア"),
    ("スプラスピナー", "ジャンプビーコン", "ウルトラショット"),
    ("バレルスピナー", "スプリンクラー", "ホップソナー"),
    ("バレルスピナー", "ポイントセンサー", "テイオウイカ"),
    ("ハイドラント", "ロボットボム", "ナイスダマ"),
    ("ハイドラント", "トラップ", "スミナガシート"),
    ("ハイドラント", "スプリンクラー", "グレートバリア"),
    ("クーゲルシュライバー", "タンサンボム", "ジェットパック"),
    ("クーゲルシュライバー", "ポイントセンサー", "キューインキ"),
    ("ノーチラス", "ポイントセンサー", "アメフラシ"),
    ("ノーチラス", "キューバンボム", "ウルトラショット"),
    ("イグザミナー", "カーリングボム", "エナジースタンド"),
    ("イグザミナー", "スプラッシュボム", "カニタンク"),

    # マニューバー
    ("スプラマニューバー", "キューバンボム", "カニタンク"),
    ("スプラマニューバー", "カーリングボム", "ウルトラチャクチ"),
    ("スプラマニューバー", "タンサンボム", "グレートバリア"),
    ("スパッタリー", "ジャンプビーコン", "エナジースタンド"),
    ("スパッタリー", "トーピード", "サメライド"),
    ("スパッタリー", "スプラッシュボム", "メガホンレーザー5.1ch"),
    ("デュアルスイーパー", "スプラッシュボム", "ホップソナー"),
    ("デュアルスイーパー", "ジャンプビーコン", "デコイチラシ"),
    ("デュアルスイーパー", "ポイントセンサー", "スミナガシート"),
    ("ケルビン525", "スプラッシュシールド", "ナイスダマ"),
    ("ケルビン525", "ポイントセンサー", "ウルトラショット"),
    ("クアッドホッパー", "ロボットボム", "サメライド"),
    ("クアッドホッパー", "スプリンクラー", "ショクワンダー"),
    ("ガエンFF", "トラップ", "メガホンレーザー5.1ch"),
    ("ガエンFF", "クイックボム", "トリプルトルネード"),

    # シェルター
    ("パラシェルター", "スプリンクラー", "トリプルトルネード"),
    ("パラシェルター", "ロボットボム", "ジェットパック"),
    ("キャンピングシェルター", "ジャンプビーコン", "キューインキ"),
    ("キャンピングシェルター", "トラップ", "ウルトラショット"),
    ("キャンピングシェルター", "ポイズンミスト", "デコイチラシ"),
    ("スパイガジェット", "トラップ", "サメライド"),
    ("スパイガジェット", "トーピード", "スミナガシート"),
    ("スパイガジェット", "カーリングボム", "メガホンレーザー5.1ch"),
    ("24式張替傘", "ラインマーカー", "グレートバリア"),
    ("24式張替傘", "ポイズンミスト", "ウルトラチャクチ"),

    # ワイパー
    ("ドライブワイパー", "トーピード", "ウルトラハンコ"),
    ("ドライブワイパー", "ジャンプビーコン", "マルチミサイル"),
    ("ドライブワイパー", "カーリングボム", "ウルトラショット"),
    ("ジムワイパー", "クイックボム", "ショクワンダー"),
    ("ジムワイパー", "ポイズンミスト", "カニタンク"),
    ("ジムワイパー", "ロボットボム", "ナイスダマ"),
    ("デンタルワイパー", "キューバンボム", "グレートバリア"),
    ("デンタルワイパー", "スプラッシュシールド", "ジェットパック"),

    # ストリンガー
    ("トライストリンガー", "ポイズンミスト", "メガホンレーザー5.1ch"),
    ("トライストリンガー", "スプリンクラー", "デコイチラシ"),
    ("トライストリンガー", "ラインマーカー", "ジェットパック"),
    ("LACT-450", "カーリングボム", "マルチミサイル"),
    ("LACT-450", "クイックボム", "サメライド"),
    ("LACT-450", "トーピード", "ナイスダマ"),
    ("フルイドV", "ポイントセンサー", "ウルトラハンコ"),
    ("フルイドV", "スプラッシュシールド", "ホップソナー")
]

# 高速でチェックできるようにリストをセットに変換
excluded_kits_set = set(excluded_kits)

all_combinations = list(itertools.product(main_weapons_list, sub_weapons_list, special_weapons_list))


# --- データベース初期化関数 (SQLAlchemy版) ---
def init_db_postgres():
    with app.app_context():
        print("Initializing database...")
        db.create_all() # テーブルが存在しない場合のみ作成

        num_combinations = len(all_combinations)
        count = db.session.query(Votes).count()

        if count < num_combinations:
            print(f"Votes table is incomplete. Found {count}/{num_combinations}. Populating...")
            # 既存のIDをセットとして取得
            existing_ids = {v.weapon_id for v in db.session.query(Votes.weapon_id).all()}
            
            # 足りないIDのオブジェクトをリストに追加
            new_votes = []
            for i in range(num_combinations):
                if i not in existing_ids:
                    new_votes.append(Votes(weapon_id=i, vote_count=0))
            
            # 新しいオブジェクトを一括で追加
            if new_votes:
                db.session.bulk_save_objects(new_votes)
                db.session.commit()
                print(f"Added {len(new_votes)} new vote entries.")
        else:
            print("Database is already initialized.")

# --- ルーティング ---

@app.route('/')
def index():
    # (フィルター/ソート条件の取得は変更なし)
    page = request.args.get('page', 1, type=int)
    type_filter = request.args.get('type', 'all')
    sub_filter = request.args.get('sub', 'all')
    special_filter = request.args.get('special', 'all')
    sort_order = request.args.get('sort', 'default')
    
    current_filters = { 'type': type_filter, 'sub': sub_filter, 'special': special_filter, 'sort': sort_order }

    # SQLAlchemyで投票数を取得
    votes_rows = db.session.query(Votes).all()
    votes_dict = {row.weapon_id: row.vote_count for row in votes_rows}

    # (絞り込み、ソート、ページ分けのロジックはほぼ変更なし)
    filtered_weapons = []
    for i, (main, sub, special) in enumerate(all_combinations):
        current_kit = (main.get('name'), sub.get('name'), special.get('name'))
        if current_kit in excluded_kits_set:
            continue
        if (type_filter == 'all' or main.get('type') == type_filter) and \
           (sub_filter == 'all' or sub.get('name') == sub_filter) and \
           (special_filter == 'all' or special.get('name') == special_filter):
            filtered_weapons.append({
                "id": i, "main": main, "sub": sub, "special": special,
                "vote_count": votes_dict.get(i, 0)
            })
    
    if sort_order == 'votes_desc':
        filtered_weapons.sort(key=lambda x: x['vote_count'], reverse=True)
    elif sort_order == 'votes_asc':
        filtered_weapons.sort(key=lambda x: x['vote_count'])

    per_page = 100
    start = (page - 1) * per_page
    end = start + per_page
    paginated_weapons = filtered_weapons[start:end]
    total_pages = math.ceil(len(filtered_weapons) / per_page)

    # (プルダウンメニュー用のリスト作成は変更なし)
    weapon_types = []
    # (中略)
    sub_weapon_names = [sub.get('name') for sub in sub_weapons_list]
    special_weapon_names = [special.get('name') for special in special_weapons_list]

    return render_template(
        'index.html',
        weapons=paginated_weapons,
        weapon_types=weapon_types,
        sub_weapons=sub_weapon_names,
        special_weapons=special_weapon_names,
        current_page=page,
        total_pages=total_pages,
        current_filters=current_filters
    )


@app.route('/vote', methods=['POST'])
@limiter.limit("30 per minute")
def vote():
    data = request.get_json()
    weapon_id = data.get('weapon_id')

    if weapon_id is None:
        return jsonify({'success': False, 'error': 'Weapon ID is missing'}), 400

    try:
        # SQLAlchemyで投票数を更新
        vote_entry = db.session.get(Votes, weapon_id)
        if vote_entry:
            vote_entry.vote_count += 1
            db.session.commit()
            return jsonify({'success': True, 'new_vote_count': vote_entry.vote_count})
        else:
            return jsonify({'success': False, 'error': 'Weapon ID not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/ranking')
def ranking():
    return render_template('ranking.html')


@app.route('/api/ranking_data')
def ranking_data():
    offset = request.args.get('offset', 0, type=int)
    limit = 100

    # SQLAlchemyでランキングデータを取得
    votes_rows = db.session.query(Votes).order_by(Votes.vote_count.desc(), Votes.weapon_id.asc()).limit(limit).offset(offset).all()
    
    ranking_results = []
    for row in votes_rows:
        weapon_id = row.weapon_id
        main, sub, special = all_combinations[weapon_id]
        ranking_results.append({
            "main": main, "sub": sub, "special": special,
            "vote_count": row.vote_count
        })

    return jsonify(ranking_results)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/_initialize_database_manually_123abc') # ← 秘密のURL
def init_db_route():
    try:
        init_db_postgres()
        return "Database initialized successfully!"
    except Exception as e:
        return f"An error occurred: {str(e)}"

# --- アプリケーションの実行 ---
#if __name__ == '__main__':
    init_db_postgres() # 起動時にデータベースを初期化
    app.run(debug=False)