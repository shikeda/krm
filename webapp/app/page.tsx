'use client';

import { useState, useCallback } from 'react';
import Link from 'next/link';
import type { SearchResult } from '@/lib/types';

export default function HomePage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searched, setSearched] = useState(false);

  const handleSearch = useCallback(async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setSearched(true);
    try {
      const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error ?? 'Search failed');
      }
      const data = await res.json();
      setResults(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, [query]);

  return (
    <main className="max-w-4xl mx-auto px-4 py-8 w-full">
      <h1 className="text-2xl font-bold mb-2 text-center">
        観智院本類聚名義抄（KRM）検索
      </h1>
      <p className="text-center text-sm text-gray-500 mb-6">
        見出し字・定義文・和訓を全文検索できます
      </p>

      <form onSubmit={handleSearch} className="flex gap-2 mb-6">
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
      </form>

      {error && (
        <div className="bg-red-50 border border-red-300 text-red-700 rounded px-4 py-3 mb-4">
          エラー: {error}
        </div>
      )}

      {searched && !loading && !error && (
        <p className="text-sm text-gray-500 mb-3">
          {results.length > 0
            ? `${results.length} 件の結果（最大50件）`
            : '検索結果が見つかりませんでした。'}
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
    </main>
  );
}
