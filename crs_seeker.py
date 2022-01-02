from bs4 import BeautifulSoup as bs
from bs4.element import ResultSet, Tag
from typing import NewType
from os import system, name


Chance = float # Percentage probability of being chosen for the class.
ClassesType = NewType('ClassesType', list[tuple[ResultSet[Tag], Chance]])

# Keywords found in the Remarks section of a course that makes the course available.
allowed_restrictions = ['DCS', 'BS CS']


def clear_screen():
    system('cls' if name == 'nt' else 'clear')

def add_to_classes(classes: ClassesType, class_fields: ResultSet[Tag]):
    assert isinstance(class_fields[5].b, Tag), f'Not tag.'
    
    try:
        available = float(class_fields[5].b.text)
    except ValueError:
        return
        
    demand = float(class_fields[6].text)

    chance: Chance = 0.0 # Default is zero if available is zero.
    if int(available) != 0:
        if int(demand) == 0:
            chance = 99999.99 # Highest value since there is no demand but there are available slots.
        else:
            chance = round((available / demand) * 100, 2)

    classes.append((class_fields, chance))    

def main() -> None:
    html_lines: list[str] = []

    # Convert HTML input into a BeautifulSoup.
    print('Input the source code of the webpage of the chosen preenlistment class list\n' + 
          '(Can be viewed by pressing Ctrl+U on the target webpage): ')
    while True:
        line = input()

        html_lines.append(line) 
        if line == '</html>':
            break
    clear_screen() 

    html: str = '\n'.join(html_lines)
    s = bs(html, 'html.parser')

    classes = ClassesType([])

    # Group available classes
    for tr in s.find_all('tr'):
        if tr.get_attribute_list('class') in [['tr_odd'], ['tr_even']]:
            class_fields: ResultSet[Tag] = tr.find_all('td')

            if len(class_fields) < 7: # Not a valid class.
                continue

            remarks: str = class_fields[4].text

            # Allow a class based on a specific keyword within the remarks section.
            for allowed in allowed_restrictions:
                if allowed in remarks:
                    add_to_classes(classes, class_fields)
                    continue

            # 'For' in the remarks 'usually' imply the course is college-specific,
            # so we include the course if 'For' is not found in its remarks.
            if 'For' not in remarks:
                add_to_classes(classes, class_fields)
                

    # Print classes with the highest chances.
    while True:
        nclasses = int(input(f'\nNumber of classes to show (Max is {len(classes)}): '))

        if nclasses <= len(classes):
            break
        else:
            print('Cannot exceed max available classes.')

    classes.sort(key= lambda x: x[1], reverse= True)

    print('\nTop available classes based on chance of acquiring a slot' + 
          '(Note: some classes may actually not be available, check the Remarks Section):\n')
    print('╔' + '═' * 5 + '╦' + '═' * 12 + '╦' + '═' * 28 + '╦' + '═' * 29 + 
          '╦' + '═' * 55 + '╦' + '═' * 10 + '╗')
    print('║  N  ║ Class Code ║        Instructor/s        ║        Schedule/Room' + 
          '        ║                        Remarks                        ║  Chance  ║')
    print('╠' + '═' * 5 + '╬' + '═' * 12 + '╬' + '═' * 28 + '╬' + '═' * 29 + 
          '╬' + '═' * 55 + '╬' + '═' * 10 + '╣')
    for i in range(nclasses):
        index = str(i+1).center(5)

        # If the class contains both a lab and lecture component, print only the lab component.
        class_code = classes[i][0][0].get_text('$').split('$')[0]
        class_code = class_code.center(12)

        instructor = classes[i][0][1].get_text('$').split('$')[-1]
        if len(instructor) > 24:
            instructor = instructor[:24] + '...'
        instructor = instructor.center(28)

        schedroom = classes[i][0][3].get_text('$').split('$')[0]
        schedroom = schedroom.center(29)

        remarks = classes[i][0][4].text.strip()
        if len(remarks) > 50:
            remarks = remarks[:50] + '...'
        elif not len(remarks): 
            remarks = 'None'
        remarks = remarks.center(55)

        chance_ = str(classes[i][1]) + ' %'
        chance_ = chance_.center(10)

        print(f'║{index}║{class_code}║{instructor}║{schedroom}║{remarks}║{chance_}║')
        if i != nclasses - 1:
            print('║' + '-' * 5 + '║' + '-' * 12 + '║' + '-' * 28 + '║' + 
                  '-' * 29 + '║' + '-' * 55 + '║' + '-' * 10 + '║')

    print('╚' + '═' * 5 + '╩' + '═' * 12 + '╩' + '═' * 28 + '╩' + '═' * 29 + 
          '╩' + '═' * 55 + '╩' + '═' * 10 + '╝')   


if __name__ == '__main__':
    main()
