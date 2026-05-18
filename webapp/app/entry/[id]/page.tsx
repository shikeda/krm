'use client';

import { use, useEffect, useState } from 'react';
import Link from 'next/link';
import type { EntryDetail } from '@/lib/types';

export default function EntryPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [entry, setEntry] = useState<EntryDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetch(`/api/entry/${encodeURIComponent(id)}`)
      .then(async (res) => {
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.error ?? 'Not found');
        }
        return res.json();
      })
      .then((data: EntryDetail) => {
        setEntry(data);
        setLoading(false);
      })
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : String(err));
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-8">
        <p className="text-gray-500">読み込み中...</p>
      </main>
    );
  }

  if (error || !entry) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-300 text-red-700 rounded px-4 py-3 mb-4">
          エラー: {error ?? '項目が見つかりませんでした'}
        </div>
        <Link href="/" className="text-blue-600 hover:underline">← 検索に戻る</Link>
      </main>
    );
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      <div className="mb-4">
        <Link href="/" className="text-blue-600 hover:underline text-sm">
          ← 検索に戻る
        </Link>
      </div>

      {/* Main entry info */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <div className="flex items-start gap-4 mb-4">
          <div>
            <span className="text-4xl font-bold">{entry.hanzi_entry}</span>
            {entry.original_entry && entry.original_entry !== '〇' && (
              <span className="ml-3 text-xl text-gray-500">（原字形: {entry.original_entry}）</span>
            )}
          </div>
          <div className="ml-auto text-right">
            <span className="text-xs font-mono text-gray-500 block">{entry.entry_id}</span>
            <span className="text-xs text-gray-500 block">{entry.source_id}</span>
          </div>
        </div>

        <dl className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
          <div>
            <dt className="text-gray-500 text-xs">巻名</dt>
            <dd className="font-medium">{entry.volume_name}</dd>
          </div>
          <div>
            <dt className="text-gray-500 text-xs">部首</dt>
            <dd className="font-medium">{entry.radical_name}</dd>
          </div>
          <div>
            <dt className="text-gray-500 text-xs">巻・部首インデックス</dt>
            <dd className="font-mono text-xs">{entry.volume_radical_index}</dd>
          </div>
          <div>
            <dt className="text-gray-500 text-xs">漢字 ID</dt>
            <dd className="font-mono text-xs">{entry.hanzi_id}</dd>
          </div>
          <div>
            <dt className="text-gray-500 text-xs">風間書房所在</dt>
            <dd className="font-mono text-xs">{entry.kazama_location}</dd>
          </div>
          <div>
            <dt className="text-gray-500 text-xs">天理図書館所在</dt>
            <dd className="font-mono text-xs">{entry.tenri_location}</dd>
          </div>
        </dl>

        {entry.definition && (
          <div className="mt-4">
            <dt className="text-gray-500 text-xs mb-1">全定義文</dt>
            <dd className="bg-gray-50 rounded p-3 text-sm leading-relaxed break-all">
              {entry.definition}
            </dd>
          </div>
        )}

        {entry.ndl_url && (
          <div className="mt-4">
            <a
              href={entry.ndl_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block bg-green-600 text-white text-sm px-4 py-2 rounded hover:bg-green-700 transition-colors"
            >
              国立国会図書館デジタルコレクション で見る →
            </a>
          </div>
        )}
      </div>

      {/* Notes table */}
      {entry.notes.length > 0 && (
        <section className="mb-6">
          <h2 className="text-lg font-semibold mb-3 border-b border-gray-200 pb-1">
            注記一覧 ({entry.notes.length} 件)
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border border-gray-200 rounded overflow-hidden">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-3 py-2 font-semibold border-b border-gray-200 w-32">連番 ID</th>
                  <th className="text-left px-3 py-2 font-semibold border-b border-gray-200 w-28">注記種別</th>
                  <th className="text-left px-3 py-2 font-semibold border-b border-gray-200">定義要素</th>
                  <th className="text-left px-3 py-2 font-semibold border-b border-gray-200 w-36">備考</th>
                </tr>
              </thead>
              <tbody>
                {entry.notes.map((n, i) => (
                  <tr key={n.definition_seq_id} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="px-3 py-2 border-b border-gray-100 font-mono text-xs text-gray-500">
                      {n.definition_seq_id}
                    </td>
                    <td className="px-3 py-2 border-b border-gray-100 text-xs">
                      <span className="inline-block bg-blue-100 text-blue-800 rounded px-1 py-0.5">
                        {n.definition_type_name}
                      </span>
                    </td>
                    <td className="px-3 py-2 border-b border-gray-100 break-all leading-relaxed">
                      {n.definition_elements}
                    </td>
                    <td className="px-3 py-2 border-b border-gray-100 text-xs text-gray-500 break-all">
                      {n.remarks ?? ''}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Wakun table */}
      {entry.wakunList.length > 0 && (
        <section className="mb-6">
          <h2 className="text-lg font-semibold mb-3 border-b border-gray-200 pb-1">
            和訓一覧 ({entry.wakunList.length} 件)
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border border-gray-200 rounded overflow-hidden">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-3 py-2 font-semibold border-b border-gray-200 w-32">ID</th>
                  <th className="text-left px-3 py-2 font-semibold border-b border-gray-200 w-32">和訓形</th>
                  <th className="text-left px-3 py-2 font-semibold border-b border-gray-200">和訓要素</th>
                  <th className="text-left px-3 py-2 font-semibold border-b border-gray-200 w-24">標準漢字</th>
                  <th className="text-left px-3 py-2 font-semibold border-b border-gray-200 w-24">JK リンク</th>
                </tr>
              </thead>
              <tbody>
                {entry.wakunList.map((w, i) => (
                  <tr key={w.wakun_id} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="px-3 py-2 border-b border-gray-100 font-mono text-xs text-gray-500">
                      {w.wakun_id}
                    </td>
                    <td className="px-3 py-2 border-b border-gray-100 font-medium">
                      {w.wakun_form}
                    </td>
                    <td className="px-3 py-2 border-b border-gray-100 text-xs break-all">
                      {w.wakun_elements}
                    </td>
                    <td className="px-3 py-2 border-b border-gray-100 text-xs">
                      {w.wakun_standard_hanzi}
                    </td>
                    <td className="px-3 py-2 border-b border-gray-100 text-xs">
                      {w.japan_knowledge_id ? (
                        <a
                          href={`https://japanknowledge-com.ezoris.lib.hokudai.ac.jp/lib/display/?lid=${w.japan_knowledge_id}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline"
                        >
                          JK
                        </a>
                      ) : ''}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </main>
  );
}
