import { useState, type FormEvent } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { cn } from '@/app/components/ui/utils';
import { AuthLayout } from '@/components/layout/AuthLayout';
import { Field } from '@/components/common/Field';
import { Notice } from '@/components/common/Notice';
import { useAuth } from '@/context/AuthContext';
import { ROLE, ROLE_OPTIONS, roleOf, type RoleId } from '@/config/roles';
import { errorMessage } from '@/lib/format';

/** Màn 01 · Đăng nhập. */
export function LoginPage() {
  const [role, setRole] = useState<RoleId>(ROLE.BUYER);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const { login, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const registered = (location.state as { registered?: boolean } | null)?.registered;
  const selected = ROLE_OPTIONS.find((option) => option.id === role)!;

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      const user = await login(username, password);
      if (roleOf(user.role_id) !== role) {
        logout();
        setError(`Tài khoản này không có quyền ${selected.label}.`);
        return;
      }
      navigate(selected.home, { replace: true });
    } catch (err) {
      setError(errorMessage(err, 'Đăng nhập thất bại'));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout title="Đăng Nhập" description="Chọn loại đăng nhập trước khi vào hệ thống">
      <div role="radiogroup" className="mb-5 grid grid-cols-3 gap-1 rounded-lg bg-border p-1">
        {ROLE_OPTIONS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            role="radio"
            aria-checked={role === id}
            onClick={() => { setRole(id); setError(''); }}
            className={cn(
              'flex items-center justify-center gap-1.5 rounded-md px-2 py-2 text-[13px] font-semibold transition',
              role === id ? 'bg-card text-primary shadow-sm' : 'text-muted-foreground hover:text-foreground',
            )}
          >
            <Icon className="size-4 shrink-0" />
            <span className="truncate">{label}</span>
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {registered && !error && <Notice tone="success">Đăng ký thành công! Vui lòng đăng nhập.</Notice>}
        {error && <Notice tone="destructive">{error}</Notice>}

        <Field label="Tên Đăng Nhập" htmlFor="username">
          <Input id="username" placeholder="Nhập tên đăng nhập" value={username} onChange={(e) => setUsername(e.target.value)} disabled={submitting} required />
        </Field>
        <Field label="Mật Khẩu" htmlFor="password">
          <Input id="password" type="password" placeholder="Nhập mật khẩu" value={password} onChange={(e) => setPassword(e.target.value)} disabled={submitting} required />
        </Field>

        <Button type="submit" size="lg" className="w-full" disabled={submitting}>
          {submitting ? 'Đang đăng nhập...' : `Đăng Nhập ${selected.label}`}
        </Button>

        <p className="text-center text-sm text-muted-foreground">
          Chưa có tài khoản?{' '}
          <Link to="/register" className="font-bold text-primary hover:underline">Đăng ký ngay</Link>
        </p>
      </form>
    </AuthLayout>
  );
}
