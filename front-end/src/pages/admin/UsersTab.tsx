import { useEffect, useState, type FormEvent } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/app/components/ui/dialog';
import { Field, NativeSelect } from '@/components/common/Field';
import { apiService, type UserData } from '@/services/api';
import { ROLE, ROLE_OPTIONS, roleOf, type RoleId } from '@/config/roles';
import { errorMessage, MISSING } from '@/lib/format';
import { TabToolbar, tableBody, tableHead, type AdminTabProps } from './shared';

/** Màn 11 · Admin · Người dùng. */
export function UsersTab({ reloadKey, tabBar, onSuccess, onError }: AdminTabProps) {
  const [users, setUsers] = useState<UserData[]>([]);
  const [links, setLinks] = useState<Record<string, string>>({});
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    apiService.listUsers().then(setUsers).catch((err) => onError(errorMessage(err, 'Không tải được danh sách user')));
    apiService.getCustomerLinks().then(setLinks).catch(() => setLinks({}));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [reloadKey]);

  const updateRole = async (target: UserData, roleId: number) => {
    try {
      await apiService.updateUserRole(target.username, roleId);
      setUsers((prev) => prev.map((u) => (u.id === target.id ? { ...u, role_id: roleId } : u)));
      onSuccess('Đã cập nhật role');
    } catch (err) {
      onError(errorMessage(err, 'Không cập nhật được role'));
    }
  };

  const remove = async (target: UserData) => {
    if (!confirm(`Xóa user ${target.username}?`)) return;
    try {
      await apiService.deleteUser(target.id);
      setUsers((prev) => prev.filter((u) => u.id !== target.id));
      onSuccess('Đã xóa user');
    } catch (err) {
      onError(errorMessage(err, 'Không xóa được user'));
    }
  };

  return (
    <>
      <TabToolbar tabBar={tabBar}>
        <Button onClick={() => setAdding(true)}><Plus /> Thêm user</Button>
      </TabToolbar>

      <div className="overflow-x-auto rounded-[10px] bg-card shadow-card">
        <table className="w-full text-sm">
          <thead className={tableHead}>
            <tr><th>Username</th><th>Email</th><th>Role</th><th>customer_id liên kết</th><th className="w-20">Action</th></tr>
          </thead>
          <tbody className={tableBody}>
            {users.map((u) => (
              <tr key={u.id}>
                <td className="font-semibold">{u.username}</td>
                <td>{u.email}</td>
                <td>
                  <NativeSelect value={roleOf(u.role_id)} onChange={(e) => updateRole(u, Number(e.target.value))} className="h-9 w-44">
                    {ROLE_OPTIONS.map((r) => <option key={r.id} value={r.id}>{r.label}</option>)}
                  </NativeSelect>
                </td>
                {/* Gán khi pipeline H&M ghi Recommendations */}
                <td className="font-mono text-xs text-muted-foreground" title={links[u.id]}>{links[u.id] ? `${links[u.id].slice(0, 12)}…` : MISSING}</td>
                <td>
                  <button onClick={() => remove(u)} className="rounded-md p-2 text-danger hover:bg-danger-soft" aria-label={`Xóa ${u.username}`}>
                    <Trash2 className="size-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <AddUserDialog
        open={adding}
        onClose={() => setAdding(false)}
        onCreated={(user) => { setUsers((prev) => [...prev, user]); onSuccess('Đã thêm user'); }}
        onError={onError}
      />
    </>
  );
}

function AddUserDialog({ open, onClose, onCreated, onError }: { open: boolean; onClose: () => void; onCreated: (user: UserData) => void; onError: (message: string) => void }) {
  const empty = { username: '', email: '', password: '', role: ROLE.BUYER as RoleId };
  const [form, setForm] = useState(empty);
  const [saving, setSaving] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    try {
      // Không có endpoint tạo user cho admin → dùng /auth/register rồi đổi role.
      const created = await apiService.register({ username: form.username, email: form.email, password: form.password });
      if (form.role !== ROLE.BUYER) await apiService.updateUserRole(created.username, form.role);
      onCreated({ ...created, role_id: form.role });
      setForm(empty);
      onClose();
    } catch (err) {
      onError(errorMessage(err, 'Không thêm được user'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(next) => !next && onClose()}>
      <DialogContent>
        <DialogHeader><DialogTitle className="text-xl font-bold">Thêm user</DialogTitle></DialogHeader>
        <form onSubmit={submit} className="space-y-4">
          <Field label="Username" htmlFor="new-username"><Input id="new-username" required value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} /></Field>
          <Field label="Email" htmlFor="new-email"><Input id="new-email" type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></Field>
          <Field label="Mật khẩu" htmlFor="new-password"><Input id="new-password" type="password" minLength={6} required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></Field>
          <Field label="Role" htmlFor="new-role">
            <NativeSelect id="new-role" value={form.role} onChange={(e) => setForm({ ...form, role: Number(e.target.value) as RoleId })}>
              {ROLE_OPTIONS.map((r) => <option key={r.id} value={r.id}>{r.label}</option>)}
            </NativeSelect>
          </Field>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>Hủy</Button>
            <Button type="submit" disabled={saving}>{saving ? 'Đang lưu...' : 'Lưu'}</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
