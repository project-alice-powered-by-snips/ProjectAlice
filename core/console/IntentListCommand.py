import click

#TODO module has to be required when intent is given
@click.command(name='intent:list')
@click.option('--module', '-m', help='Show more data about specific module')
@click.option('--intent', '-i', help='Show more data about specific intent')
@click.option('--full', '-f', is_flag=True, help='Display full description instead of truncated one')
def IntentListCommand(module: bool, intent: bool, full: bool):
	"""List intents and utterances for a given module"""

	import random
	from terminaltables import DoubleTable
	from core.base.SuperManager import SuperManager
	
	superManager = SuperManager(None)
	superManager.initManagers()
	superManager.onStart()

	samkillaManager = superManager.getManager('SamkillaManager')
	languageManager = superManager.getManager('LanguageManager')

	_slotTypesModulesValues, _intentsModulesValues, _intentNameSkillMatching = samkillaManager.getDialogTemplatesMaps(
		runOnAssistantId=languageManager.activeSnipsProjectId,
		languageFilter=languageManager.activeLanguage
	)

	DESCRIPTION_MAX = 100
	found = False

	if intent:
		TABLE_DATA = [['Utterances of ' + intent + ' intent']]
		table_instance = DoubleTable(TABLE_DATA)
		click.secho('\n{}\n'.format(table_instance.table), fg='yellow')

		TABLE_DATA = [['Utterances']]
		table_instance = DoubleTable(TABLE_DATA)

		for dtIntentName, dtModuleName in _intentNameSkillMatching.items():
			if dtIntentName == intent and dtModuleName == module:
				found = True

				for utterance in _intentsModulesValues[dtIntentName]['utterances']:
					if not full:
						utterance = (utterance[:DESCRIPTION_MAX] + '..') if len(utterance) > DESCRIPTION_MAX else utterance

					TABLE_DATA.append([ utterance or '-' ])

	elif module:
		TABLE_DATA = [['Intents of ' + module + ' module']]
		table_instance = DoubleTable(TABLE_DATA)
		click.secho('\n{}\n'.format(table_instance.table), fg='yellow')

		TABLE_DATA = [['Intent', 'Description', 'Default']]
		table_instance = DoubleTable(TABLE_DATA)

		for dtIntentName, dtModuleName in _intentNameSkillMatching.items():
			if dtModuleName == module:
				found = True
				tDesc = _intentsModulesValues[dtIntentName]['__otherattributes__']['description']
				tEnabledByDefault = _intentsModulesValues[dtIntentName]['__otherattributes__']['enabledByDefault']

				if not full:
					tDesc = (tDesc[:DESCRIPTION_MAX] + '..') if len(tDesc) > DESCRIPTION_MAX else tDesc

				TABLE_DATA.append([
					dtIntentName,
					tDesc or '-',
					'X' if tEnabledByDefault else ''
				])

	else:
		TABLE_DATA = [['All Alice intents']]
		table_instance = DoubleTable(TABLE_DATA)
		click.secho('\n{}\n'.format(table_instance.table), fg='yellow')

		TABLE_DATA = [['Intent', 'D', 'Description', 'Example']]
		table_instance = DoubleTable(TABLE_DATA)
		table_instance.justify_columns[1] = 'center'
		found = True

		for dtIntentName in _intentNameSkillMatching:
			tDesc = _intentsModulesValues[dtIntentName]['__otherattributes__']['description']
			tEnabledByDefault = _intentsModulesValues[dtIntentName]['__otherattributes__']['enabledByDefault']

			tUtterance = random.choice(list(_intentsModulesValues[dtIntentName]['utterances']))

			if not full:
				tDesc = (tDesc[:DESCRIPTION_MAX] + '..') if len(tDesc) > DESCRIPTION_MAX else tDesc
				tUtterance = (tUtterance[:DESCRIPTION_MAX] + '..') if len(tUtterance) > DESCRIPTION_MAX else tUtterance

			TABLE_DATA.append([
				dtIntentName,
				'X' if tEnabledByDefault else '',
				tDesc or '-',
				tUtterance or '-'
			])

	if not found:
		click.echo('\nNo intent found\n', err=True)
	else:
		click.echo(table_instance.table)
