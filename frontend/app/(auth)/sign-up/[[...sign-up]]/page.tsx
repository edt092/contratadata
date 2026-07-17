import { SignUp } from '@clerk/nextjs'

export default function SignUpPage() {
  return (
    <main style={{ display: 'flex', justifyContent: 'center', padding: '64px 20px' }}>
      <SignUp />
    </main>
  )
}
