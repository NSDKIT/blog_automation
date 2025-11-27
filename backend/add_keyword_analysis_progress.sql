-- キーワード分析の進捗状況を記録するカラムを追加
-- SupabaseダッシュボードのSQL Editorで実行してください

ALTER TABLE articles ADD COLUMN IF NOT EXISTS keyword_analysis_progress JSONB;

-- 進捗状況の構造:
-- {
--   "status_check": true/false,        -- ステータスがkeyword_analysisかどうか
--   "openai_generation": true/false,   -- OpenAIでキーワード生成が成功したか
--   "dataforseo_fetch": true/false,    -- DataForSEOでデータ取得が成功したか
--   "scoring_completed": true/false,   -- スコアリングが完了したか
--   "current_step": "status_check" | "openai_generation" | "dataforseo_fetch" | "scoring" | "completed",
--   "error_message": "エラーメッセージ（エラー時）"
-- }

