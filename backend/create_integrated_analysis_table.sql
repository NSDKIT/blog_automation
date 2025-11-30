-- 統合分析結果を保存するテーブル
-- SupabaseダッシュボードのSQL Editorで実行してください

CREATE TABLE IF NOT EXISTS integrated_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    keyword VARCHAR(255) NOT NULL,
    location_code INTEGER NOT NULL DEFAULT 2840,
    language_code VARCHAR(10) NOT NULL DEFAULT 'ja',
    main_keyword JSONB,
    related_keywords JSONB,
    summary_stats JSONB,
    recommended_strategy JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_integrated_analyses_user_id ON integrated_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_integrated_analyses_keyword ON integrated_analyses(keyword);
CREATE INDEX IF NOT EXISTS idx_integrated_analyses_created_at ON integrated_analyses(created_at DESC);

-- updated_atを自動更新するトリガー
CREATE TRIGGER update_integrated_analyses_updated_at BEFORE UPDATE ON integrated_analyses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) の設定
ALTER TABLE integrated_analyses ENABLE ROW LEVEL SECURITY;

-- 自分の統合分析結果のみ読み取り可能
CREATE POLICY "integrated_analyses_select_own" ON integrated_analyses
    FOR SELECT USING (auth.uid()::text = user_id::text);

-- 自分の統合分析結果のみ作成可能
CREATE POLICY "integrated_analyses_insert_own" ON integrated_analyses
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

-- 自分の統合分析結果のみ更新可能
CREATE POLICY "integrated_analyses_update_own" ON integrated_analyses
    FOR UPDATE USING (auth.uid()::text = user_id::text);

-- 自分の統合分析結果のみ削除可能
CREATE POLICY "integrated_analyses_delete_own" ON integrated_analyses
    FOR DELETE USING (auth.uid()::text = user_id::text);

