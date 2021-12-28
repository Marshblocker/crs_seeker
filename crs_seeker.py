from bs4 import BeautifulSoup as bs
from bs4.element import ResultSet, Tag
from typing import NewType


Chance = float # Percentage probability of being chosen for the class.
ClassesType = NewType('ClassesType', list[tuple[ResultSet[Tag], Chance]])

allowed_restrictions = ['DCS', 'BS CS'] # Modify if needed.


def add_to_classes(classes: ClassesType, class_fields: ResultSet[Tag]):
    assert isinstance(class_fields[5].b, Tag), f'Not tag.'
    available = float(class_fields[5].b.text)
    demand = float(class_fields[6].text)

    chance: Chance = 0.0 # Default is zero if available is zero.
    if available != 0:
        if int(demand) == 0:
            chance = 99999.99 # Highest value since there is no demand but there are available slots.
        else:
            chance = round((available / demand) * 100, 2)

    classes.append((class_fields, chance))    

def main() -> None:
    html_lines: list[str] = []

    # Convert HTML input into a BeautifulSoup.
    print('Input the source code of the webpage of the chosen preenlistment class \n(Can be viewed by pressing Ctrl+U): ')
    while True:
        line = input()

        html_lines.append(line) 
        if line == '</html>':
            break

    html: str = '\n'.join(html_lines)
    s = bs(html, 'html.parser')

    classes = ClassesType([])

    # Group available classes
    L = s.find_all('tr')
    for i, tr in enumerate(L):
        if tr.get_attribute_list('class') in [['tr_odd'], ['tr_even']]:
            class_fields: ResultSet[Tag] = tr.find_all('td')

            if len(class_fields) < 7: # Not a valid class.
                continue

            restriction: str = class_fields[4].text

            # Allow a class based on a specific keyword within the remarks section.
            for allowed in allowed_restrictions:
                if allowed in restriction:
                    add_to_classes(classes, class_fields)
                    continue

            # Allow a class not restricted to a specific college.
            if 'For' not in restriction:
                add_to_classes(classes, class_fields)
                

    while True:
        nclasses = int(input(f'\nNumber of classes to show (Max is {len(classes)}): '))

        if nclasses > len(classes):
            print('Cannot exceed max available classes.')
            continue
        else:
            break

    classes.sort(key= lambda x: x[1], reverse= True)

    # Print classes with the highest chances.
    print('\nTop available classes based on chance of acquiring a slot (Note: some classes may actually not be available, check the Remarks Section):\n')
    print('╔' + '═' * 12 + '╦' + '═' * 28 + '╦' + '═' * 29 + '╦' + '═' * 55 + '╦' + '═' * 10 + '╗')
    print('║ Class Code ║        Instructor/s        ║        Schedule/Room        ║                        Remarks                        ║  Chance  ║')
    print('╠' + '═' * 12 + '╬' + '═' * 28 + '╬' + '═' * 29 + '╬' + '═' * 55 + '╬' + '═' * 10 + '╣')
    for i in range(nclasses):
        # If the class contains both a lab and lecture component, print only the lab component.
        class_code = classes[i][0][0].get_text('$').split('$')[0]

        instructor = classes[i][0][1].get_text('$').split('$')[-1]
        if len(instructor) > 24:
            instructor = instructor[:24] + '...'

        schedroom = classes[i][0][3].get_text('$').split('$')[0]

        remarks = classes[i][0][4].text.strip()
        if len(remarks) > 50:
            remarks = remarks[:50] + '...'
        elif not len(remarks):
            remarks = 'None'

        chance_ = str(classes[i][1]) + ' %'
        print(f'║{class_code.center(12)}║{instructor.center(28)}║{schedroom.center(29)}║{remarks.center(55)}║{chance_.center(10)}║')
    print('╚' + '═' * 12 + '╩' + '═' * 28 + '╩' + '═' * 29 + '╩' + '═' * 55 + '╩' + '═' * 10 + '╝')        


if __name__ == '__main__':
    main()