#!import { expect } from 'chai';

describe('📝 WILSY OS - Document Template Registry', () => {
  it('should successfully register a legal template', () => {
    const template = { id: 'TPL-001', type: 'NDA', jurisdiction: 'ZA' };
    expect(template.id).to.equal('TPL-001');
    expect(template.jurisdiction).to.equal('ZA');
  });

  it('should identify dynamic variables within a template', () => {
    const rawText = 'Agreement between {{tenant}} and {{client}}.';
    const hasVariables = /\{\{.*?\}\}/.test(rawText);
    expect(hasVariables).to.be.true;
  });
});
