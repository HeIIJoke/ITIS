export const permissions = Object.freeze({
  guest: ['public'],
  student: ['public', 'account'],
  teacher: ['public', 'account'],
  admin: ['public', 'account', 'admin'],
});
export function canAccess(account, access = 'public') {
  if (access === 'guest') return !account;
  if (access === 'account') return Boolean(account);
  return (permissions[account?.role] ?? permissions.guest).includes(access);
}
