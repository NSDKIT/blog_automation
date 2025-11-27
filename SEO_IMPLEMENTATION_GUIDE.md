# SEO対策実装ガイド

## 実装完了内容

### ✅ 実装済み機能

1. **DataForSEO API統合**
   - SERP API（検索エンジン結果ページ50件分析）
   - Keywords Data API（キーワード検索ボリューム・競合度分析）
   - Content Generation API（メタタグ・サブトピック生成）

2. **データベース拡張**
   - `articles`テーブルにSEO関連カラムを追加
   - SERP分析データ、キーワードデータ、メタタグ、構造化データを保存

3. **ワークフロー統合**
   - 記事生成時に自動でSEO分析を実行
   - SERP分析 → キーワード調査 → 記事生成 → メタタグ生成 → 構造化データ生成

4. **構造化データ生成**
   - Article Schema
   - FAQPage Schema
   - BreadcrumbList Schema
   - Organization Schema

5. **フロントエンド拡張**
   - 記事作成フォームにSEO設定項目を追加
   - 記事詳細画面にSEO分析結果を表示

---

## セットアップ手順

### 1. DataForSEO APIアカウントの取得

1. [DataForSEO](https://dataforseo.com/)でアカウントを作成
2. API認証情報（login/password）を取得

### 2. 環境変数の設定

#### バックエンド（`.env`ファイル）

```env
# DataForSEO API認証情報
DATAFORSEO_LOGIN=your_login
DATAFORSEO_PASSWORD=your_password
```

#### または、ユーザー設定から管理

設定画面（`/settings`）で以下を登録：
- `dataforseo_login`: DataForSEOのログインID
- `dataforseo_password`: DataForSEOのパスワード

### 3. データベースマイグレーション

SupabaseのSQL Editorで以下を実行：

```sql
-- SEO関連カラムの追加（supabase_tables.sqlに含まれています）
ALTER TABLE articles ADD COLUMN IF NOT EXISTS serp_data JSONB;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS serp_headings_analysis JSONB;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS serp_common_patterns JSONB;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS serp_faq_items JSONB;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS keyword_volume_data JSONB;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS related_keywords JSONB;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS keyword_difficulty JSONB;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS meta_title TEXT;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS meta_description TEXT;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS subtopics JSONB;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS content_structure JSONB;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS search_intent VARCHAR(50);
ALTER TABLE articles ADD COLUMN IF NOT EXISTS target_location VARCHAR(50) DEFAULT 'Japan';
ALTER TABLE articles ADD COLUMN IF NOT EXISTS device_type VARCHAR(20) DEFAULT 'mobile';
ALTER TABLE articles ADD COLUMN IF NOT EXISTS structured_data JSONB;
```

---

## 使用方法

### 記事生成時のSEO設定

1. **記事作成ページ**（`/articles/new`）にアクセス
2. 基本情報を入力：
   - キーワード
   - ターゲット層
   - 記事の種類
   - 重要キーワード（1-3個）
3. **SEO設定セクション**で以下を設定：
   - **検索意図**: 情報収集 / 購買検討 / 比較検討 / 問題解決
   - **検索地域**: 日本 / 東京 / 大阪
   - **デバイスタイプ**: モバイル / デスクトップ
   - **サブキーワード**: カンマ区切りで複数入力可能
4. 「記事を生成」ボタンをクリック

### 生成されるSEOデータ

記事生成時に自動で以下が生成・保存されます：

- **SERP分析結果**: 上位50件の検索結果を分析
- **キーワードデータ**: 検索ボリューム、競合度、CPC
- **メタタグ**: SEO最適化されたメタタイトル・メタディスクリプション
- **サブトピック**: 関連トピック10個
- **FAQ項目**: People Also Askから抽出
- **構造化データ**: Schema.org形式のJSON-LD

### 記事詳細画面での確認

記事詳細画面（`/articles/{id}`）で以下を確認できます：

- **メタタグ**: タイトル・ディスクリプションの文字数チェック
- **キーワード情報**: 検索ボリューム、競合度、CPC
- **SERP分析結果**: 見出しパターンの統計
- **FAQ項目**: 競合記事でよく使われる質問
- **推奨サブトピック**: 記事に含めるべきトピック

---

## APIコスト目安

### DataForSEO API料金（参考）

- **SERP API（Advanced、depth=50）**: 約$0.05-0.10/リクエスト
- **Keywords Data API**: 約$0.01-0.02/キーワード
- **Content Generation API**: 約$0.01/リクエスト

### 1記事あたりのコスト

- SERP分析: $0.05-0.10
- キーワード調査（4キーワード）: $0.04-0.08
- メタタグ生成: $0.01
- サブトピック生成: $0.01

**合計**: 約$0.11-0.20/記事（約15-30円）

### 月間コスト試算（100記事想定）

- **最小**: $11（約1,650円）
- **最大**: $20（約3,000円）

---

## トラブルシューティング

### DataForSEO APIエラー

**エラー**: "DataForSEO設定が完了していません"

**解決方法**:
1. 設定画面（`/settings`）でDataForSEO認証情報を登録
2. または、環境変数に`DATAFORSEO_LOGIN`と`DATAFORSEO_PASSWORD`を設定

### SERP分析が失敗する

**原因**: APIクォータ超過、ネットワークエラー

**対処**: 
- エラーが発生しても記事生成は続行されます
- 後で手動で再分析することも可能（将来実装予定）

### キーワードデータが取得できない

**原因**: 禁止カテゴリのキーワード（武器、タバコ、ドラッグ等）

**対処**: 
- 別のキーワードを使用
- エラーが発生しても記事生成は続行されます

---

## 今後の拡張予定

1. **検索順位追跡**: 定期的に順位をチェック
2. **コンテンツ更新提案**: 順位低下時の改善提案
3. **A/Bテスト**: タイトル・メタタグの複数案生成
4. **レポート機能**: 月次SEOレポートの自動生成
5. **競合分析**: より詳細な競合サイト分析

---

## 注意事項

- DataForSEO APIは有料サービスです。使用前に料金プランを確認してください
- APIコールにはレート制限があります（毎分2000回）
- 大量の記事生成時は、バッチ処理やキャッシュを活用してください
- 生成されたメタタグは必ず確認・調整してください（自動生成のため完璧ではない場合があります）

---

## 参考リンク

- [DataForSEO API ドキュメント](https://dataforseo.com/apis)
- [Schema.org ドキュメント](https://schema.org/)
- [Google 検索セントラル](https://developers.google.com/search)

