describe('Token Tests', () => {
  const items = [
    { name: 'Web bug', extraFields: null },
    { name: 'DNS', extraFields: null },
    { name: 'QR code', extraFields: null },
    { name: 'MySQL', extraFields: null },
    { name: 'Log4shell', extraFields: null },
    { name: 'Microsoft Excel document', extraFields: null },
    { name: 'Microsoft Word document', extraFields: null },
    { name: 'SVN', extraFields: null },
    { name: 'Unique email address', extraFields: null },
    { name: 'Acrobat Reader PDF', extraFields: null },
    { name: 'Windows Folder', extraFields: null },
    { name: 'Kubeconfig', extraFields: null },
    { name: 'WireGuard VPN', extraFields: null },
    { name: 'Azure Entra ID login', extraFields: null },
    { name: 'Fast redirect', extraFields: () => cy.get('#redirect_url').type('www.google.pt') },
    { name: 'Slow redirect', extraFields: () => cy.get('#redirect_url').type('www.google.pt') },
    { name: 'Sensitive command', extraFields: () => cy.get('#cmd_process').type('test.exe') },
    { name: 'Web image',
  extraFields: () => {
    cy.get('input[type="file"]').selectFile('cypress/fixtures/logo.png', { force: true })
  }
},
    { name: 'Microsoft SQL Server', extraFields: () => {
      cy.get('#update').click()
      cy.get('#sql_server_table_name').type('TEST')
    }},
 { name: 'Custom EXE / binary',
  extraFields: () => {
    cy.get('input[type="file"]').selectFile('cypress/fixtures/helloWorld.dll', { force: true })
  }
},
    { name: 'JS cloned website', extraFields: () => cy.get('#clonedsite').type('www.google.pt') },
    { name: 'CSS cloned website', extraFields: () => cy.get('#expected_referrer').type('www.google.pt') },
    { name: 'Fake App', extraFields: () => cy.get('[for="whatsapp"]').click() }
  ]

  items.forEach(item => {
    it(`should execute the test for ${item.name}`, () => {
      const domain = Cypress.env('TEST_DOMAIN')
      cy.visit(`https://${domain}/`)
 
      cy.contains(item.name).click()

      cy.get('#email').type('sara@thinkst.com')
      cy.get('#memo').type('test')

      // Execute additional fields commands if they exist
      if (item.extraFields) {
        item.extraFields()
      }
      // Take a screenshot for the filled state
      cy.screenshot(`snapshots/${item.name.toLowerCase().replace(/ /g, '_')}/filled`, { clip: { x: 0, y: 0, width: 890, height: 640 } })

      // Click on 'Create Token' and take a screenshot
      cy.contains('Create Canarytoken').click()
      cy.screenshot(`snapshots/${item.name.toLowerCase().replace(/ /g, '_')}/token_created`, { clip: { x: 0, y: 0, width: 890, height: 640 } })

      // Click on 'How to use' and take a screenshot
      cy.contains('How to use').click()
      cy.screenshot(`snapshots/${item.name.toLowerCase().replace(/ /g, '_')}/how_to_use`, { clip: { x: 0, y: 0, width: 890, height: 640 } })

      // Take a screenshot and click on 'Got it!'
      cy.screenshot(`snapshots/${item.name.toLowerCase().replace(/ /g, '_')}/manage_token`, { clip: { x: 0, y: 0, width: 890, height: 640 } })
      cy.contains('Got it!').click()

      // Take a screenshot and click on 'Manage Canarytoken'
      cy.screenshot(`snapshots/${item.name.toLowerCase().replace(/ /g, '_')}/manage_token`, { clip: { x: 0, y: 0, width: 890, height: 640 } })
      cy.contains('Manage Canarytoken').click()

      // Click on 'ALERTS HISTORY' and take a screenshot
      cy.get('.justify-end')
       .contains('Alerts History').click()
      cy.screenshot(`snapshots/${item.name.toLowerCase().replace(/ /g, '_')}/token_history`, { clip: { x: 0, y: 0, width: 890, height: 640 } })

    })
  })
})
