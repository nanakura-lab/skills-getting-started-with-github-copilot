"""
FastAPI エンドポイントのユニットテスト

より詳細な検証とエッジケースのテスト
"""

import pytest


class TestActivityValidation:
    """アクティビティのバリデーション関連テスト"""
    
    def test_activity_has_required_fields(self, client):
        """アクティビティに必須フィールドが含まれているか確認"""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"{activity_name} に {field} が不足"
                assert activity_data[field] is not None
    
    def test_max_participants_is_positive_integer(self, client):
        """max_participants は正の整数か確認"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0
    
    def test_participants_is_list_of_strings(self, client):
        """participants はリスト型で、要素が文字列か確認"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list)
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)


class TestSignupEdgeCases:
    """サインアップのエッジケーステスト"""
    
    def test_signup_with_empty_email(self, client):
        """空のメールアドレスでサインアップ"""
        response = client.post(
            "/activities/テニス部/signup",
            params={"email": ""}
        )
        # 空文字列でも一度は追加される（バリデーションなし）
        assert response.status_code in [200, 400]
    
    def test_signup_with_special_characters_in_email(self, client):
        """特殊文字を含むメールアドレスでサインアップ"""
        special_email = "test+special@example.com"
        response = client.post(
            "/activities/テニス部/signup",
            params={"email": special_email}
        )
        assert response.status_code == 200
    
    def test_signup_multiple_times_same_user(self, client):
        """同じユーザーが複数回サインアップ試行"""
        email = "repeat_test@example.com"
        
        # 1回目：成功
        response1 = client.post(
            "/activities/テニス部/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # 2回目：失敗
        response2 = client.post(
            "/activities/テニス部/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
    
    def test_signup_different_activities_same_user(self, client):
        """同じユーザーが異なるアクティビティにサインアップ"""
        email = "multi_activity@example.com"
        
        # テニス部にサインアップ
        response1 = client.post(
            "/activities/テニス部/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # バドミントン部にサインアップ
        response2 = client.post(
            "/activities/バドミントン部/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # 両方に登録されているか確認
        response = client.get("/activities")
        data = response.json()
        assert email in data["テニス部"]["participants"]
        assert email in data["バドミントン部"]["participants"]


class TestCancelEdgeCases:
    """キャンセルのエッジケーステスト"""
    
    def test_cancel_and_resign_up(self, client):
        """キャンセルして再度サインアップ"""
        email = "cancel_resign@example.com"
        
        # サインアップ
        client.post(
            "/activities/テニス部/signup",
            params={"email": email}
        )
        
        # キャンセル
        client.delete(
            "/activities/テニス部/signup",
            params={"email": email}
        )
        
        # 再度サインアップ
        response = client.post(
            "/activities/テニス部/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    def test_cancel_multiple_times(self, client):
        """同じユーザーが複数回キャンセル試行"""
        email = "repeat_cancel@example.com"
        
        # サインアップ
        client.post(
            "/activities/テニス部/signup",
            params={"email": email}
        )
        
        # 1回目キャンセル：成功
        response1 = client.delete(
            "/activities/テニス部/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # 2回目キャンセル：失敗
        response2 = client.delete(
            "/activities/テニス部/signup",
            params={"email": email}
        )
        assert response2.status_code == 400


class TestParticipantCountTracking:
    """参加者数の追跡テスト"""
    
    def test_participant_count_increases_on_signup(self, client):
        """サインアップで参加者数が増える"""
        # 初期参加者数
        response = client.get("/activities")
        initial_count = len(response.json()["テニス部"]["participants"])
        
        # サインアップ
        client.post(
            "/activities/テニス部/signup",
            params={"email": "count_test1@example.com"}
        )
        
        # 参加者数確認
        response = client.get("/activities")
        new_count = len(response.json()["テニス部"]["participants"])
        assert new_count == initial_count + 1
    
    def test_participant_count_decreases_on_cancel(self, client):
        """キャンセルで参加者数が減る"""
        email = "count_test_cancel@example.com"
        
        # サインアップ
        client.post(
            "/activities/テニス部/signup",
            params={"email": email}
        )
        
        # 参加者数
        response = client.get("/activities")
        count_with_signup = len(response.json()["テニス部"]["participants"])
        
        # キャンセル
        client.delete(
            "/activities/テニス部/signup",
            params={"email": email}
        )
        
        # 参加者数確認
        response = client.get("/activities")
        count_after_cancel = len(response.json()["テニス部"]["participants"])
        assert count_after_cancel == count_with_signup - 1


class TestErrorMessages:
    """エラーメッセージのテスト"""
    
    def test_activity_not_found_message(self, client):
        """アクティビティが見つからないときのエラーメッセージ"""
        response = client.post(
            "/activities/存在しないクラス/signup",
            params={"email": "test@example.com"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_duplicate_signup_error_message(self, client):
        """重複サインアップのエラーメッセージ"""
        response = client.post(
            "/activities/チェス部/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        detail = response.json()["detail"]
        assert "already signed up" in detail
        assert "michael@mergington.edu" in detail
    
    def test_full_activity_error_message(self, client):
        """満員のエラーメッセージ"""
        activity_name = "チェス部"
        
        # 満員にする
        for i in range(10):
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": f"fill{i}@example.com"}
            )
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "overflow@example.com"}
        )
        assert response.status_code == 400
        assert "Activity is full" in response.json()["detail"]
