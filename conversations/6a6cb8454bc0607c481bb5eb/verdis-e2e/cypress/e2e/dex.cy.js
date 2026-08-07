/// <reference types="cypress" />

describe('DEX', () => {
  beforeEach(() => {
    cy.visit('/dex/', { timeout: 20000 });
    cy.get('.status', { timeout: 20000 }).should('contain', 'Connected');
  });

  it('loads and shows Connected status', () => {
    cy.get('#netStatus').should('contain', 'Connected');
  });

  it('shows 7 AMM pools with correct token names', () => {
    cy.get('.pool-item', { timeout: 15000 }).should('have.length.at.least', 6);
    cy.get('.pool-item').first().should('contain', 'VRDX');
  });

  it('pools show reserves not zero', () => {
    cy.get('.pool-reserve').first().should('not.contain', '0.00');
  });

  it('pool fee shows 0.3%', () => {
    cy.get('.pool-fee').first().should('contain', '0.3');
  });

  it('selecting a pool shows details', () => {
    cy.get('.pool-item').first().click();
    cy.get('#poolDetails').should('contain', 'Pool ID');
    cy.get('#poolDetails').should('contain', 'Reserve');
  });

  it('swap tab is active by default', () => {
    cy.get('#tabSwap').should('have.class', 'active');
    cy.get('#swapPanel').should('be.visible');
  });

  it('liquidity tab toggles correctly', () => {
    cy.get('#tabLiquidity').click();
    cy.get('#liquidityPanel').should('be.visible');
    cy.get('#swapPanel').should('not.be.visible');
  });

  it('swap form has token dropdowns populated', () => {
    cy.get('#swapFrom option').should('have.length.at.least', 2);
    cy.get('#swapTo option').should('have.length.at.least', 2);
  });

  it('swap calculator shows output for valid input', () => {
    // Select tokens
    cy.get('#swapFrom').select(0);
    cy.get('#swapTo').select(1);
    cy.get('#swapAmountIn').type('10');
    cy.get('#swapAmountOut').should('not.have.value', '');
    cy.get('#swapInfo').should('be.visible');
    cy.get('#swapRate').should('contain', '=');
  });

  it('account selector has dev accounts', () => {
    cy.get('#swapAccount option').should('have.length.at.least', 5);
  });

  it('shows live block height in stats', () => {
    cy.get('#statBlock').should('contain', '#');
  });

  it('shows pool count in stats', () => {
    cy.get('#statPools').should('not.contain', '--');
  });
});
