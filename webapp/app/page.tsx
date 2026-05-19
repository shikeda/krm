'use client';

import { useState, useCallback, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import type { SearchResult, SearchResponse } from '@/lib/types';

function SearchPage() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [query, setQuery] = useState(searchParams.get('q') ?? '');
  const [itaiji, setItaiji] = useState(searchParams.get('itaiji') === '1');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searched, setSearched] = useState(false);
  const [hintOpen, setHintOpen] = useState(false);

  const runSearch = useCallback(async (q: string, useItaiji: boolean) => {
    if (!q.trim()) return;
    setLoading(true);
    setError(null);
    setSearched(true);
    try {
      const url = `/api/search?q=${encodeURIComponent(q)}${useItaiji ? '&itaiji=1' : ''}`;
      const res = await fetch(url);
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error ?? 'Search failed');
      }
      const data: SearchResponse = await res.json();
      setResults(data.results);
      setTotalCount(data.total_count);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
      setResults([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  }, []);

  // ページロード時に URL パラメータがあれば自動検索
  useEffect(() => {
    const q = searchParams.get('q');
    const it = searchParams.get('itaiji') === '1';
    if (q) {
      setQuery(q);
      setItaiji(it);
      runSearch(q, it);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSearch = useCallback(async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;
    // URL に検索状態を反映してリロード後も復元できるようにする
    const params = new URLSearchParams();
    params.set('q', query);
    if (itaiji) params.set('itaiji', '1');
    router.push(`?${params.toString()}`, { scroll: false });
    await runSearch(query, itaiji);
  }, [query, itaiji, router, runSearch]);

  return (
    <main className="max-w-4xl mx-auto px-4 py-8 w-full flex flex-col min-h-screen">
      <div className="flex-1">
        <h1 className="text-2xl font-bold mb-2 text-center">
          観智院本類聚名義抄（KRM）検索
        </h1>
        <p className="text-center text-sm text-gray-500 mb-6">
          見出し字・定義文・和訓を全文検索できます
        </p>

        <form onSubmit={handleSearch} className="mb-6">
          <div className="flex gap-2 mb-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="例: 阿，こころ，観智"
              className="flex-1 border border-gray-300 rounded px-3 py-2 text-base focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={loading}
              className="bg-blue-600 text-white px-5 py-2 rounded hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {loading ? '検索中...' : '検索'}
            </button>
          </div>
          <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer select-none w-fit">
            <input
              type="checkbox"
              checked={itaiji}
              onChange={(e) => setItaiji(e.target.checked)}
              className="w-4 h-4 accent-blue-600"
            />
            異体字を含めて検索
          </label>
        </form>

        <div className="mb-4 border border-gray-200 rounded">
          <button
            type="button"
            onClick={() => setHintOpen(o => !o)}
            className="w-full flex items-center justify-between px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 transition-colors"
          >
            <span className="font-medium">検索のヒント</span>
            <span className="text-gray-400 text-xs">{hintOpen ? '▲ 閉じる' : '▼ 開く'}</span>
          </button>
          {hintOpen && (
            <ol className="px-4 pb-4 pt-1 text-sm text-gray-600 space-y-2 list-decimal list-inside border-t border-gray-200">
              <li>
                見出し字・定義文・和訓を横断して全文検索します。検索フィールドの個別指定はできません。
              </li>
              <li>
                二字以上の見出し字は「仿／佛」のように ／ で区切って格納されています。
                複字見出しを検索するには、一字ずつ個別に検索するか、／ を挟んで「仿／佛」と入力してください。
              </li>
              <li>
                「異体字を含めて検索」をチェックすると、新旧字体の違いを意識せず検索できます（例: 亜→亞）。
                <br />
                <span className="text-gray-400 text-xs">
                  異体字データ: 人間文化研究機構 異体漢字対応テーブル（CC-BY 4.0）
                </span>
              </li>
              <li>
                スペース（全角・半角）で区切って複数語を入力すると OR 検索になります（例:「ヒト ひと」）。
              </li>
              <li>
                和訓をひらがな辞書形で検索できます（例:「ひと」「ゆく」）。
                カタカナで入力すると定義文中の音注・和訓表記にヒットします。活用語は終止形で入力してください。
              </li>
              <li>
                編者注（remarks）は検索対象外です。
              </li>
              <li>
                表示件数は最大50件です。51件以上ヒットした場合は「X件中50件を表示しています」と表示されます。検索語を絞り込んで再検索してください。
              </li>
            </ol>
          )}
        </div>

        {error && (
          <div className="bg-red-50 border border-red-300 text-red-700 rounded px-4 py-3 mb-4">
            エラー: {error}
          </div>
        )}

        {searched && !loading && !error && (
          <p className="text-sm text-gray-500 mb-3">
            {totalCount === 0
              ? '検索結果が見つかりませんでした。'
              : totalCount > results.length
              ? `${totalCount}件中${results.length}件を表示しています`
              : `${totalCount}件`}
          </p>
        )}

        {results.length > 0 && (
          <div className="border border-gray-200 rounded overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-700">
                <tr>
                  <th className="text-left px-3 py-2 font-semibold border-b border-gray-200 w-24">ID</th>
                  <th className="text-left px-3 py-2 font-semibold border-b border-gray-200 w-20">見出し字</th>
                  <th className="text-left px-3 py-2 font-semibold border-b border-gray-200 w-28">巻名・部首</th>
                  <th className="text-left px-3 py-2 font-semibold border-b border-gray-200">定義（先頭80字）</th>
                </tr>
              </thead>
              <tbody>
                {results.map((r, i) => (
                  <tr
                    key={r.entry_id}
                    className={`hover:bg-blue-50 cursor-pointer transition-colors ${i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}
                  >
                    <td className="px-3 py-2 border-b border-gray-100">
                      <Link href={`/entry/${r.entry_id}`} className="text-blue-600 hover:underline font-mono text-xs">
                        {r.entry_id}
                      </Link>
                    </td>
                    <td className="px-3 py-2 border-b border-gray-100">
                      <Link href={`/entry/${r.entry_id}`} className="font-bold text-lg hover:text-blue-700">
                        {r.hanzi_entry}
                      </Link>
                    </td>
                    <td className="px-3 py-2 border-b border-gray-100 text-gray-600 text-xs">
                      <Link href={`/entry/${r.entry_id}`} className="block">
                        {r.volume_name}・{r.radical_name}
                      </Link>
                    </td>
                    <td className="px-3 py-2 border-b border-gray-100 text-gray-700">
                      <Link href={`/entry/${r.entry_id}`} className="block truncate">
                        {r.definition_snippet}
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <footer className="mt-12 pt-4 border-t border-gray-200 text-xs text-gray-400 text-center">
        異体字データ：
        <a
          href="https://www.bridge.nihu.jp/researchdata/file/20221125_ITOBYb"
          target="_blank"
          rel="noopener noreferrer"
          className="underline hover:text-gray-600"
        >
          人間文化研究機構 異体漢字対応テーブル
        </a>
        （CC-BY 4.0）
      </footer>
    </main>
  );
}

export default function HomePage() {
  return (
    <Suspense>
      <SearchPage />
    </Suspense>
  );
}
