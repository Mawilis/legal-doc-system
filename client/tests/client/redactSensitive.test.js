/* eslint-disable */
import { describe, it, expect } from 'vitest'

// Redaction utilities
const redactSensitive = (data) => {
  if (!data) return data
  
  if (typeof data === 'string') {
    if (data.includes('@')) {
      return '[REDACTED-EMAIL]'
    }
    if (data.match(/^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/)) {
      return '[REDACTED-PHONE]'
    }
    return data
  }
  
  if (Array.isArray(data)) {
    return data.map(item => redactSensitive(item))
  }
  
  if (typeof data === 'object') {
    const redacted = {}
    for (const [key, value] of Object.entries(data)) {
      if (['email', 'phone', 'password', 'ssn', 'idNumber'].includes(key)) {
        redacted[key] = '[REDACTED]'
      } else {
        redacted[key] = redactSensitive(value)
      }
    }
    return redacted
  }
  
  return data
}

const maskEmail = (email) => {
  if (!email || !email.includes('@')) return email
  const [localPart, domain] = email.split('@')
  
  if (localPart.length <= 1) {
    return `${localPart}***@${domain}`
  } else if (localPart.length === 2) {
    return `${localPart[0]}*${localPart[1]}@${domain}`
  } else {
    return `${localPart[0]}***${localPart[localPart.length-1]}@${domain}`
  }
}

const maskPhone = (phone) => {
  if (!phone) return phone
  const visible = phone.slice(-4)
  // Count digits only for masking
  const digits = phone.replace(/\D/g, '').length
  const asterisks = digits - 4
  return '*'.repeat(asterisks) + visible
}

describe('redactSensitive', () => {
  it('redacts email addresses', () => {
    const input = { email: 'user@example.com' }
    const output = redactSensitive(input)
    expect(output.email).toBe('[REDACTED]')
  })

  it('redacts phone numbers', () => {
    const input = { phone: '+27123456789' }
    const output = redactSensitive(input)
    expect(output.phone).toBe('[REDACTED]')
  })

  it('handles nested objects', () => {
    const input = {
      user: {
        name: 'John Doe',
        contact: {
          email: 'john@example.com',
          phone: '+27123456789'
        }
      }
    }
    const output = redactSensitive(input)
    
    expect(output.user.name).toBe('John Doe')
    expect(output.user.contact.email).toBe('[REDACTED]')
    expect(output.user.contact.phone).toBe('[REDACTED]')
  })

  it('handles arrays', () => {
    const input = {
      users: [
        { email: 'user1@example.com' },
        { email: 'user2@example.com' }
      ]
    }
    const output = redactSensitive(input)
    
    expect(output.users[0].email).toBe('[REDACTED]')
    expect(output.users[1].email).toBe('[REDACTED]')
  })

  it('maskEmail produces correct masked emails', () => {
    expect(maskEmail('test@example.com')).toBe('t***t@example.com')
    expect(maskEmail('a@b.co.za')).toBe('a***@b.co.za')
    expect(maskEmail('ab@domain.com')).toBe('a*b@domain.com')
    expect(maskEmail('abc@domain.com')).toBe('a***c@domain.com')
    expect(maskEmail('')).toBe('')
    expect(maskEmail(null)).toBe(null)
  })

  it('maskPhone produces correct masked phones', () => {
    expect(maskPhone('+27123456789')).toBe('*******6789') // 11 digits total, show last 4 -> 7 asterisks
    expect(maskPhone('0123456789')).toBe('******6789') // 10 digits total, show last 4 -> 6 asterisks
    expect(maskPhone('1234')).toBe('1234') // No masking if 4 digits or less
  })
});
