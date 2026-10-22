import { useState, type ChangeEvent, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { AuthLayout } from '@/components/layout/AuthLayout';
import { Field, NativeSelect } from '@/components/common/Field';
import { Notice } from '@/components/common/Notice';
import { useAuth } from '@/context/AuthContext';
import type { RegisterData } from '@/services/api';
import { errorMessage } from '@/lib/format';

/** Màn 02 · Đăng ký. */
export function RegisterPage() {
  const [form, setForm] = useState<RegisterData>({ username: '', email: '', password: '', gender: '', age: undefined });
  const [confirmPassword, setConfirmPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: name === 'age' ? (value ? Number(value) : undefined) : value }));
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (form.password.length < 6) return setError('Mật khẩu phải có ít nhất 6 ký tự.');
    if (form.password !== confirmPassword) return setError('Mật khẩu xác nhận không khớp.');

    setSubmitting(true);
    setError('');
    try {
      await register({ ...form, gender: form.gender || undefined });
      navigate('/login', { state: { registered: true } });
    } catch (err) {
      setError(errorMessage(err, 'Đăng ký thất bại'));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout title="Đăng Ký" description="Tạo tài khoản mới để bắt đầu">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <Notice tone="destructive">{error}</Notice>}

        <Field label="Tên Đăng Nhập" htmlFor="username">
          <Input id="username" name="username" placeholder="Chọn tên đăng nhập" value={form.username} onChange={handleChange} disabled={submitting} required />
        </Field>
        <Field label="Email" htmlFor="email">
          <Input id="email" name="email" type="email" placeholder="your@email.com" value={form.email} onChange={handleChange} disabled={submitting} required />
        </Field>
        <Field label="Mật Khẩu" htmlFor="password">
          <Input id="password" name="password" type="password" placeholder="Ít nhất 6 ký tự" value={form.password} onChange={handleChange} disabled={submitting} required />
        </Field>
        <Field label="Xác Nhận Mật Khẩu" htmlFor="confirmPassword">
          <Input id="confirmPassword" type="password" placeholder="Nhập lại mật khẩu" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} disabled={submitting} required />
        </Field>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Giới Tính" htmlFor="gender">
            <NativeSelect id="gender" name="gender" value={form.gender} onChange={handleChange} disabled={submitting}>
              <option value="">Chọn</option>
              <option value="male">Nam</option>
              <option value="female">Nữ</option>
              <option value="other">Khác</option>
            </NativeSelect>
          </Field>
          <Field label="Tuổi" htmlFor="age">
            <Input id="age" name="age" type="number" min={1} max={120} placeholder="25" value={form.age ?? ''} onChange={handleChange} disabled={submitting} />
          </Field>
        </div>

        <Button type="submit" size="lg" className="w-full" disabled={submitting}>
          {submitting ? 'Đang đăng ký...' : 'Đăng Ký'}
        </Button>

        <p className="text-center text-sm text-muted-foreground">
          Đã có tài khoản?{' '}
          <Link to="/login" className="font-bold text-primary hover:underline">Đăng nhập</Link>
        </p>
      </form>
    </AuthLayout>
  );
}
