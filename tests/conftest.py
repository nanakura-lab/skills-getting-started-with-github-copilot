"""
共通テストフィクスチャ
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# src ディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """FastAPI TestClient を返すフィクスチャ"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """各テスト前後で activities をリセット"""
    # テスト前：初期状態を設定
    original_activities = {
        "チェス部": {
            "description": "チェスの戦略を学び、チェストーナメントで競う",
            "schedule": "金曜日, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "プログラミングクラス": {
            "description": "プログラミングの基礎を学び、ソフトウェアプロジェクトを構築する",
            "schedule": "火曜日と木曜日, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "体育科": {
            "description": "体育教育とスポーツ活動",
            "schedule": "月曜日、水曜日、金曜日, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "テニス部": {
            "description": "テニス技術を習得し、試合に参加する",
            "schedule": "水曜日と土曜日, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": []
        },
        "バドミントン部": {
            "description": "バドミントンの基本と戦術を学ぶ",
            "schedule": "月曜日と金曜日, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": []
        },
        "美術部": {
            "description": "絵画、彫刻、デジタルアートなどの芸術を学ぶ",
            "schedule": "木曜日, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": []
        },
        "音楽部": {
            "description": "楽器演奏と音楽理論を学ぶ",
            "schedule": "火曜日と金曜日, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": []
        },
        "ロボット工学クラブ": {
            "description": "ロボット工学とプログラミングを学び、ロボット競技に参加する",
            "schedule": "水曜日, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "数学オリンピッククラブ": {
            "description": "数学の問題解決スキルを磨き、オリンピック大会に参加する",
            "schedule": "土曜日, 10:00 AM - 12:00 PM",
            "max_participants": 12,
            "participants": []
        }
    }
    
    # 既存のデータをクリアして、初期状態を設定
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # テスト後：クリーンアップ
    activities.clear()
    activities.update(original_activities)
