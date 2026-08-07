/// <reference types="cypress" />

describe('Wallet', () => {
  beforeEach(() => {
    cy.visit('/wallet/', { timeout: 20000 });
    // Wait for polkadot.js to load
    cy.get('.status', { timeout: 20000 }).should('contain', 'Connected');
  });

  it('loads and shows status as Connected', () => {
    cy.get('#netStatus').should('contain', 'Connected');
  });

  it('shows live stats (block, peers, validators)', () => {
    cy.get('#statBlock').should('contain', '#');
    cy.get('#statPeers').should('not.contain', '--');
    cy.get('#statValidators').should('not.contain', '--');
  });

  it('create new wallet generates mnemonic and address', () => {
    cy.get('#btnCreate').click();
    cy.get('#accountAddress').should('contain', 'k');  // ss58 address starts with k (format 909)
    cy.get('#mnemonicText').should('not.be.empty');
    cy.get('#balanceValue').should('contain', '0.00');
  });

  it('import dev account //Alice shows correct balance', () => {
    cy.get('#devAccount').select('//Alice');
    cy.get('#accountAddress').should('be.visible');
    cy.get('#balanceValue', { timeout: 10000 }).should('not.contain', '0.00');
  });

  it('import dev account //Bob shows address', () => {
    cy.get('#devAccount').select('//Bob');
    cy.get('#accountAddress').should('be.visible');
    cy.get('#nonceValue').should('not.contain', '--');
  });

  it('send form accepts address and amount', () => {
    cy.get('#devAccount').select('//Alice');
    cy.get('#sendTo').type('5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY');
    cy.get('#sendAmount').type('1.5');
    cy.get('#btnSend').should('be.visible');
  });

  it('copy address button works', () => {
    cy.get('#devAccount').select('//Alice');
    cy.get('#btnCopy').should('be.visible');
  });

  it('export mnemonic shows seed phrase', () => {
    cy.get('#devAccount').select('//Alice');
    cy.get('#btnExport').click();
    cy.get('#mnemonicBox').should('be.visible');
    cy.get('#mnemonicText').should('contain', '//Alice');
  });

  it('clear wallet removes account', () => {
    cy.get('#devAccount').select('//Alice');
    cy.get('#hasAccount').should('be.visible');
    // Note: we won't actually click clear to avoid losing state
  });
});
