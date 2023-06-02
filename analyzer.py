"""Module for analyzing the results of the miner."""

import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

from analyzer.yml_analyzer import YmlAnalyzer


platforms = ['github_actions', 'travis_ci']
creation_date_normalizers = {
    "github_actions": "2018-01-01",
    "travis_ci": "2011-01-01"
}

def create_timeline_graph(repo):
    fig = plt.figure()

    for n, workflow_file in enumerate(repo['workflow_files']):
        dates = []
        additions = []
        deletions = []

        for commit in reversed(workflow_file['commits']):
            if commit['file']:
                dates.append(commit['date'])
                additions.append(commit['file']['additions'])
                deletions.append(commit['file']['deletions'] * -1)


        x = [mdates.datestr2num(d) for d in dates]

        ax = fig.add_subplot(len(repo['workflow_files']), 1, n + 1)

        ax.bar(x, deletions, width=1, color='r')
        ax.bar(x, additions, width=1, color='g')

        ax.set_title(workflow_file['path'])

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        
        fig.autofmt_xdate()

    fig.suptitle(repo['repo'])
    plt.show()

def create_age_to_ci_intro_graph(repos):
    x = []
    y = []
    y_normalized = []
    c = []

    for _, repo in repos.items():
        repo_creation = repo['created_at']

        for n, workflow_file in enumerate(repo['workflow_files']): 
            workflow_creation = workflow_file['commits'][len(workflow_file['commits']) - 1]['date']

            x.append(mdates.date2num(datetime.now()) - mdates.datestr2num(repo_creation))
            y.append(mdates.datestr2num(workflow_creation) - mdates.datestr2num(repo_creation))

            creation_normalized = max(mdates.datestr2num(repo_creation), mdates.datestr2num(creation_date_normalizers[workflow_file['platform']]))
            y_normalized.append(mdates.datestr2num(workflow_creation) - creation_normalized)

            c.append('red' if workflow_file['platform'] == 'github_actions' else 'blue')

    fig = plt.figure()
    plt.suptitle('Repository age vs introduction of CI config files')
    fig.supylabel('Time untill CI introduction (days)')
    fig.supxlabel('Repository age (days)')

    ax1 = plt.subplot(211)
    ax1.scatter(x, y, c=c)
    ax1.set_xlim(max(x), min(x))

    ax2 = plt.subplot(212, sharex=ax1)
    ax2.scatter(x, y_normalized, c=c)
    ax2.set_xlabel('')
    ax2.set_ylabel('Normalized')
    ax2.set_xlim(max(x), min(x))

    plt.savefig('create_age_to_ci_intro.png', transparent=True)
    plt.show()

def avg_time_to_ci_intro(repos):
    

    data = []

    for platform in platforms:
        time_to_ci = []
        time_to_ci_normalized = []

        for repo_name, repo in repos.items():
            repo_creation = repo['created_at']

            for n, workflow_file in enumerate(repo['workflow_files']):
                if workflow_file['platform'] == platform:

                    workflow_creation = workflow_file['commits'][len(workflow_file['commits']) - 1]['date']
                    workflow_age = mdates.datestr2num(workflow_creation) - mdates.datestr2num(repo_creation)
                    time_to_ci.append(workflow_age)

                    creation_normalized = max(mdates.datestr2num(repo_creation), mdates.datestr2num(creation_date_normalizers[platform]))
                    workflow_age_normalized = mdates.datestr2num(workflow_creation) - creation_normalized
                    time_to_ci_normalized.append(workflow_age_normalized)
        
        data.append(time_to_ci)
        data.append(time_to_ci_normalized)

        avg_time_to_ci = sum(time_to_ci) / len(time_to_ci)
        print(f"{platform}: {avg_time_to_ci} days")

        avg_time_to_ci_normalized = sum(time_to_ci_normalized) / len(time_to_ci_normalized)
        print(f"{platform}: {avg_time_to_ci_normalized} days (normalized)")

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.boxplot(data)
    ax.set_xticklabels(['GitHub Actions', 'GitHub Actions (normalized)', 'TravisCI', 'TravisCI (normalized)'])
    ax.tick_params(axis='x', labelsize=6)

    plt.title("Introduction of CI config files per platform")
    plt.xlabel("CI platform")
    plt.ylabel('Time untill CI introduction (days)')

    plt.savefig('avg_time_to_ci_intro.png', transparent=True)
    plt.show()


def create_trigger_pie_chart(triggers):
    """Creates a pie chart of the triggers used in GitHub Actions workflows"""

    fig = plt.figure()
    ax = fig.add_subplot(111)

    trigger_types = list(triggers.keys())
    trigger_counts = [trigger['count'] for trigger in list(triggers.values())]

    ax.pie(trigger_counts, labels=trigger_types, startangle=90)
    ax.axis('equal')

    # create legend with values only
    plt.legend(loc='upper left', labels=['%1.1f%%' % s for s in trigger_counts])

    plt.title("Triggers used in GitHub Actions")

    plt.savefig('triggers_pie.png', transparent=True)
    plt.show()

def create_triggers_modifiers_pie_chart(triggers):
    """Creates a pie chart of the modifiers per trigger used in GitHub Actions workflows"""

    for trigger, trigger_data in triggers.items():
        if trigger_data['modifiers'] and len(trigger_data['modifiers']) > 0:
            fig = plt.figure()
            ax = fig.add_subplot(111)

            modifier_types = list(trigger_data['modifiers'].keys())
            modifier_counts = [modifier for modifier in list(trigger_data['modifiers'].values())]

            ax.pie(modifier_counts, labels=modifier_types, startangle=90)
            ax.axis('equal')

            # create legend with values only
            plt.legend(loc='upper left', labels=['%1.1f%%' % s for s in modifier_counts])

            plt.title(f"Modifiers used for {trigger} trigger in GitHub Actions")

            plt.savefig(f'triggers_modifiers_pie_{trigger}.png', transparent=True)
            plt.show()

def create_trigger_coocurrance_heatmap(trigger_names, trigger_coocurrance):
    """Creates a heatmap of the coocurrance of triggers in GitHub Actions workflows"""

    fig, ax = plt.subplots()

    im = ax.imshow(trigger_coocurrance)

    # We want to show all ticks...
    ax.set_xticks(np.arange(len(trigger_names)))
    ax.set_yticks(np.arange(len(trigger_names)))
    # ... and label them with the respective list entries
    ax.set_xticklabels(trigger_names)
    ax.set_yticklabels(trigger_names)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
            rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(trigger_names)):
        for j in range(len(trigger_names)):
            text = ax.text(j, i, trigger_coocurrance[i, j],
                        ha="center", va="center", color="w")

    ax.set_title("Coocurrance of triggers in GitHub Actions")
    fig.tight_layout()

    plt.savefig('triggers_coocurrance.png', transparent=True)
    plt.show()


if __name__ == '__main__':
    with open('result.json', 'r') as f:
        data = json.load(f)

        rqs = [False, True, False, False]

        # Research Question 1
        if rqs[0]:
            avg_time_to_ci_intro(data)
            create_age_to_ci_intro_graph(data)

            for repo_name, repo in data.items():
                create_timeline_graph(repo)

        # Research Question 2
        if rqs[1]:
            ymlAnalyzer = YmlAnalyzer(data)

            used_triggers = ymlAnalyzer.aggregate_triggers()

            # create_trigger_pie_chart(used_triggers)
            # create_triggers_modifiers_pie_chart(used_triggers)

            trigger_names, trigger_coocurrance = ymlAnalyzer.aggregate_triggers_coocurrance(sorted(list(used_triggers.keys())))
            create_trigger_coocurrance_heatmap(trigger_names, trigger_coocurrance)
