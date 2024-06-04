describe('Token Tests', () => {
  const items = [
    { name: 'Web bug', extraFields: null },
    { name: 'DNS', extraFields: null },
    { name: 'QR code', extraFields: null },
    { name: 'MySQL', extraFields: null },
    { name: 'AWS keys', extraFields: null },
    { name: 'Log4shell', extraFields: null },
    { name: 'Microsoft Excel document', extraFields: null },
    { name: 'Microsoft Word document', extraFields: null },
    { name: 'SVN', extraFields: null },
    { name: 'Unique email address', extraFields: null },
    { name: 'Acrobat Reader PDF document', extraFields: null },
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
    { name: 'Azure login certificate', extraFields: () => cy.get('#azure_id_cert_file_name').type('Code_Sign_Server_3.pem') },
    { name: 'Microsoft SQL Server', extraFields: () => {
      cy.get('#update').click()
      cy.get('#sql_server_table_name').type('TEST')
    }},
 { name: 'Custom exe / binary',
  extraFields: () => {
    cy.get('input[type="file"]').selectFile('cypress/fixtures/helloWorld.dll', { force: true })
  }
},
    { name: 'Cloned website', extraFields: () => cy.get('#clonedsite').type('www.google.pt') },
    { name: 'CSS cloned website', extraFields: () => cy.get('#expected_referrer').type('www.google.pt') }
  ]

  items.forEach(item => {
    it(`should execute the test for ${item.name}`, () => {
      cy.visit('https://ssl-srv72.net/nest/')

      cy.contains(item.name).click()
      
      cy.get('#1__slide').click()
      // Take a screenshot for the initial state
      cy.screenshot(`snapshots/${item.name.toLowerCase().replace(/ /g, '_')}/not_filled`, { clip: { x: 0, y: 0, width: 890, height: 640 } })

      // Perform common actions
      cy.get('#2__slide').click()
      cy.screenshot(`snapshots/${item.name.toLowerCase().replace(/ /g, '_')}/not_filled_step_2`, { clip: { x: 0, y: 0, width: 890, height: 640 } })

      cy.get('#3__slide').click()
      cy.screenshot(`snapshots/${item.name.toLowerCase().replace(/ /g, '_')}/not_filled_step_3`, { clip: { x: 0, y: 0, width: 890, height: 640 } })

      cy.get('#email').type('sara@thinkst.com')
      cy.get('#memo').type('test')

      // Execute additional fields commands if they exist
      if (item.extraFields) {
        item.extraFields()
      }
      // Take a screenshot for the filled state
      cy.screenshot(`snapshots/${item.name.toLowerCase().replace(/ /g, '_')}/filled`, { clip: { x: 0, y: 0, width: 890, height: 640 } })

      // Click on 'Create Token' and take a screenshot
      cy.contains('Create Token').click()
      cy.screenshot(`snapshots/${item.name.toLowerCase().replace(/ /g, '_')}/token_created`, { clip: { x: 0, y: 0, width: 890, height: 640 } })

      // Click on 'How to use' and take a screenshot
      cy.contains('How to use').click()
      cy.screenshot(`snapshots/${item.name.toLowerCase().replace(/ /g, '_')}/how_to_use`, { clip: { x: 0, y: 0, width: 890, height: 640 } })

      // Click on 'Manage Token' and take a screenshot
      cy.contains('Manage Token').click()
      cy.screenshot(`snapshots/${item.name.toLowerCase().replace(/ /g, '_')}/manage_token`, { clip: { x: 0, y: 0, width: 890, height: 640 } })
      
      // Click on 'Token History' and take a screenshot
      cy.contains('Token History').click()
      cy.screenshot(`snapshots/${item.name.toLowerCase().replace(/ /g, '_')}/token_history`, { clip: { x: 0, y: 0, width: 890, height: 640 } })

    })
  })
})
