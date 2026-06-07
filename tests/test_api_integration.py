"""
FastAPI 統合テスト

すべてのエンドポイントの統合テスト
"""

import pytest


class TestGetActivities:
    """GET /activities エンドポイントのテスト"""
    
    def test_get_activities_returns_all_activities(self, client):
        """すべてのアクティビティを取得できるか確認"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "チェス部" in data
        assert "プログラミングクラス" in data
    
    def test_get_activities_returns_correct_structure(self, client):
        """アクティビティの構造が正しいか確認"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["チェス部"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_get_activities_returns_participants_list(self, client):
        """participants が正しくリストに含まれているか確認"""
        response = client.get("/activities")
        data = response.json()
        
        chess_activity = data["チェス部"]
        assert isinstance(chess_activity["participants"], list)
        assert "michael@mergington.edu" in chess_activity["participants"]


class TestSignupForActivity:
    """POST /activities/{activity_name}/signup エンドポイントのテスト"""
    
    def test_signup_successful(self, client):
        """正常なサインアップ"""
        response = client.post(
            "/activities/テニス部/signup",
            params={"email": "test@example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "test@example.com" in data["message"]
    
    def test_signup_adds_participant(self, client):
        """サインアップがパーティシパントリストに追加されるか確認"""
        client.post(
            "/activities/テニス部/signup",
            params={"email": "new_participant@example.com"}
        )
        
        response = client.get("/activities")
        tennis_activity = response.json()["テニス部"]
        assert "new_participant@example.com" in tennis_activity["participants"]
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        """存在しないアクティビティへのサインアップは404エラー"""
        response = client.post(
            "/activities/存在しないクラス/signup",
            params={"email": "test@example.com"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_email_returns_400(self, client):
        """既に参加しているメールアドレスでのサインアップは400エラー"""
        response = client.post(
            "/activities/チェス部/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_full_activity_returns_400(self, client):
        """人数がいっぱいのアクティビティへのサインアップは400エラー"""
        # max_participants が 12 で、既に 2 人参加している
        activity_name = "チェス部"
        
        # 12 - 2 = 10 人分のスペース、10 人追加してみる
        for i in range(10):
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": f"student{i}@example.com"}
            )
        
        # 11 番目のサインアップは失敗
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "extra_student@example.com"}
        )
        assert response.status_code == 400
        assert "Activity is full" in response.json()["detail"]


class TestCancelSignup:
    """DELETE /activities/{activity_name}/signup エンドポイントのテスト"""
    
    def test_cancel_signup_successful(self, client):
        """正常なキャンセル"""
        # 先に新規参加者を追加
        client.post(
            "/activities/テニス部/signup",
            params={"email": "test_cancel@example.com"}
        )
        
        # キャンセルする
        response = client.delete(
            "/activities/テニス部/signup",
            params={"email": "test_cancel@example.com"}
        )
        assert response.status_code == 200
        assert "Cancelled signup" in response.json()["message"]
    
    def test_cancel_removes_participant(self, client):
        """キャンセルがパーティシパントリストから削除するか確認"""
        email = "test_participant@example.com"
        
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
        
        # 削除確認
        response = client.get("/activities")
        tennis_activity = response.json()["テニス部"]
        assert email not in tennis_activity["participants"]
    
    def test_cancel_nonexistent_activity_returns_404(self, client):
        """存在しないアクティビティからのキャンセルは404エラー"""
        response = client.delete(
            "/activities/存在しないクラス/signup",
            params={"email": "test@example.com"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_cancel_not_signed_up_returns_400(self, client):
        """参加していないメールアドレスでのキャンセルは400エラー"""
        response = client.delete(
            "/activities/テニス部/signup",
            params={"email": "not_signed_up@example.com"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_cancel_existing_participant(self, client):
        """既に参加しているメンバーのキャンセル"""
        response = client.delete(
            "/activities/チェス部/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        
        # 削除確認
        response = client.get("/activities")
        chess_activity = response.json()["チェス部"]
        assert "michael@mergington.edu" not in chess_activity["participants"]


class TestRootRedirect:
    """GET / エンドポイントのテスト"""
    
    def test_root_redirects_to_static(self, client):
        """ルートパスが /static/index.html にリダイレクトするか確認"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "static/index.html" in response.headers.get("location", "")
