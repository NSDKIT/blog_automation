# ユーザー遷移フロー

## 記事生成の完全なフロー

### ステップ1: 記事作成フォーム（`/articles/new`）

**画面**: `ArticleNew.tsx`

**ユーザー入力項目**:
- ✅ キーワード（必須）
- ✅ ターゲット層（必須）
- ✅ 記事の種類（必須）
- 使用シーン1-3（任意）
- システムプロンプト（任意）
- 重要視したいキーワード1-3（任意）
- SEO設定:
  - 検索意図（デフォルト: 情報収集）
  - 検索地域（デフォルト: Japan）
  - デバイスタイプ（デフォルト: mobile）
  - サブキーワード（任意）

**アクション**: 「記事を生成」ボタンをクリック

**遷移**: `/articles/{id}` に自動リダイレクト

---

### ステップ2: 記事詳細画面（`/articles/{id}`）

**画面**: `ArticleDetail.tsx`

**ステータス**: `keyword_analysis`（キーワード分析中）

**表示内容**:
- ローディングスピナー
- 「キーワード分析中」メッセージ
- 「この処理には約30-60秒かかります」
- 「分析が完了すると自動でキーワード選択画面に移動します」

**バックグラウンド処理**:
1. OpenAIで関連キーワード100個を生成
2. DataForSEO Labs APIで100個のキーワードを分析
3. 上位20個をGoogle Ads APIで再分析（より正確なデータ）
4. スコアリング・ソート

**ポーリング**: 2秒ごとにステータスを確認

**自動遷移**: ステータスが`keyword_selection`になったら自動でキーワード選択画面にリダイレクト

---

### ステップ3: キーワード選択画面（`/articles/{id}/keywords`）

**画面**: `KeywordSelection.tsx`

**ステータス**: `keyword_selection`（キーワード選択待ち）

**表示内容**:
- メインキーワード表示
- キーワード一覧テーブル（100個）:
  - チェックボックス
  - キーワード名
  - 検索ボリューム
  - 競合度（色分け: 緑/黄/赤）
  - CPC
  - スコア
- 検索機能
- ソート機能（スコア順/検索ボリューム順/競合度順）
- 全選択/全解除ボタン
- 選択状況表示（「選択中: X個 / 100個」）

**ユーザー操作**:
1. キーワードを検索・フィルタ
2. ソート順を変更
3. チェックボックスでキーワードを選択（複数選択可能）
4. 「選択したX個のキーワードで記事生成」ボタンをクリック

**遷移**: `/articles/{id}` に自動リダイレクト（記事生成開始）

---

### ステップ4: 記事詳細画面（`/articles/{id}`）

**画面**: `ArticleDetail.tsx`

**ステータス**: `processing`（記事生成中）

**表示内容**:
- 記事タイトル（生成中）
- 記事本文（生成中）
- ローディング表示

**バックグラウンド処理**:
1. SERP APIで競合50件を分析
2. Content Generation APIでサブトピック生成
3. AI API（OpenAI/Gemini）でタイトル・記事生成
4. Content Generation APIでメタタグ生成
5. 構造化データ生成
6. 画像選定・挿入

**ポーリング**: 2秒ごとにステータスを確認

**自動更新**: ステータスが`completed`になったら記事内容を表示

---

### ステップ5: 記事詳細画面（完了）

**画面**: `ArticleDetail.tsx`

**ステータス**: `completed`（完了）

**表示内容**:
- ✅ 記事タイトル
- ✅ 記事本文（Markdown形式、画像含む）
- ✅ SEO分析結果:
  - メタタグ（メタタイトル、メタディスクリプション）
  - キーワード情報（検索ボリューム、競合度、CPC）
  - SERP分析結果
  - FAQ項目
  - サブトピック
  - 構造化データ
- ✅ アクションボタン:
  - 編集
  - Shopifyに投稿
  - WordPressに投稿
  - 削除

---

## 遷移フローチャート

```
1. /articles/new
   ↓ ユーザーがフォームに入力
   ↓ 「記事を生成」をクリック
   
2. POST /api/articles
   ↓ 記事レコード作成（status: "keyword_analysis"）
   ↓ バックグラウンドでキーワード分析開始
   ↓
   
3. /articles/{id}
   ↓ ステータス: "keyword_analysis"
   ↓ ローディング表示
   ↓ ポーリング（2秒ごと）
   ↓
   
4. キーワード分析完了
   ↓ ステータス: "keyword_selection"
   ↓ 自動リダイレクト
   ↓
   
5. /articles/{id}/keywords
   ↓ キーワード選択画面
   ↓ ユーザーがキーワードを選択
   ↓ 「記事生成」をクリック
   ↓
   
6. POST /api/articles/{id}/select-keywords
   ↓ 選択されたキーワードを保存
   ↓ ステータス: "processing"
   ↓ バックグラウンドで記事生成開始
   ↓ 自動リダイレクト
   ↓
   
7. /articles/{id}
   ↓ ステータス: "processing"
   ↓ ローディング表示
   ↓ ポーリング（2秒ごと）
   ↓
   
8. 記事生成完了
   ↓ ステータス: "completed"
   ↓ 記事内容を表示
```

---

## ステータス一覧

| ステータス | 説明 | 画面表示 | 次のアクション |
|-----------|------|---------|---------------|
| `keyword_analysis` | キーワード分析中 | ローディング | 自動でキーワード選択画面へ |
| `keyword_selection` | キーワード選択待ち | キーワード選択画面 | ユーザーがキーワードを選択 |
| `processing` | 記事生成中 | ローディング | 自動で記事内容を表示 |
| `completed` | 完了 | 記事詳細 | 編集・投稿・削除可能 |
| `failed` | 失敗 | エラーメッセージ | 再試行または削除 |

---

## ポーリング設定

### ArticleDetail.tsx
```typescript
refetchInterval: (query) => {
  const article = query.state.data
  // キーワード分析中またはキーワード選択待ちの場合はポーリング
  if (article?.status === 'keyword_analysis' || article?.status === 'keyword_selection') {
    return 2000 // 2秒ごとにポーリング
  }
  return false
}
```

### KeywordSelection.tsx
```typescript
refetchInterval: (query) => {
  const article = query.state.data
  if (article?.status === 'keyword_analysis') {
    return 2000 // 2秒ごとにポーリング
  }
  return false
}
```

---

## 自動リダイレクト

### キーワード分析完了時
```typescript
// ArticleDetail.tsx
useEffect(() => {
  if (article?.status === 'keyword_selection' && !window.location.pathname.includes('/keywords')) {
    navigate(`/articles/${id}/keywords`)
  }
}, [article?.status, id, navigate])
```

### キーワード選択完了時
```typescript
// KeywordSelection.tsx
const selectKeywordsMutation = useMutation({
  mutationFn: (keywords: string[]) => articlesApi.selectKeywords(id!, keywords),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['article', id] })
    navigate(`/articles/${id}`) // 記事詳細画面に戻る
  },
})
```

---

## 処理時間の目安

| 処理 | 時間 | 説明 |
|------|------|------|
| キーワード分析 | 30-60秒 | OpenAI生成 + DataForSEO分析 |
| キーワード選択 | ユーザー操作 | ユーザーが選択するまで |
| 記事生成 | 60-120秒 | SERP分析 + AI生成 + メタタグ生成 |

---

## エラー処理

### キーワード分析失敗
- ステータス: `failed`
- エラーメッセージを表示
- ユーザーは再試行または削除可能

### 記事生成失敗
- ステータス: `failed`
- エラーメッセージを表示
- ユーザーは再試行または削除可能

---

## まとめ

1. **記事作成** → フォーム入力 → 「記事を生成」クリック
2. **キーワード分析** → 自動で開始 → ローディング表示
3. **キーワード選択** → 自動で遷移 → ユーザーが選択
4. **記事生成** → 自動で開始 → ローディング表示
5. **完了** → 記事内容を表示 → 編集・投稿可能

**特徴**:
- ✅ 自動遷移（ユーザー操作不要）
- ✅ ポーリングでリアルタイム更新
- ✅ ローディング表示で進捗を可視化
- ✅ エラーハンドリング完備

