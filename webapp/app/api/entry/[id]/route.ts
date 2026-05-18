import { type NextRequest } from 'next/server';
import { getEntry } from '@/lib/db';

export async function GET(_req: NextRequest, ctx: RouteContext<'/api/entry/[id]'>) {
  const { id } = await ctx.params;
  const entry = getEntry(id);
  if (!entry) return Response.json({ error: 'Not found' }, { status: 404 });
  return Response.json(entry);
}
