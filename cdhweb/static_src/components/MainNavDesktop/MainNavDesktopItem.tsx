import { MouseEvent, useId } from 'react';
import Svg from '../svg/svg';
import cx from 'classnames';
import { MainNavItemPrimary, NavItem } from '../../data-types';
import SearchForm from '../SearchForm/SearchForm';

type DesktopMenuItemProps = {
  item: MainNavItemPrimary;
  isOpen: boolean;
  onClick: (e: MouseEvent<HTMLElement>) => void;
  dropdownRef: React.RefObject<HTMLDivElement>;
};

type SubmenuItemProps = {
  item: NavItem;
  isLast?: boolean;
};

const SubmenuItem = ({ item, isLast }: SubmenuItemProps) => (
  <a
    href={item.link_url}
    className="main-nav-desktop-submenu-link"
    data-is-last={isLast || undefined}
  >
    {item.title}
  </a>
);

type SubmenuColumnsProps = {
  items: NavItem[];
};

// Split list of links into two columns,but only if the number of links meets a `threshold`.
// Yes we can do this in CSS but it feels a bit nicer if the reading order goes "top to bottom,
// left to right" rather than zig-zagging "left to right, top to bottom".
const SubmenuColumns = ({ items }: SubmenuColumnsProps) => {
  const thresholdMet = items.length > 4;
  const half = items && Math.ceil(items.length / 2);
  const col1 = items?.slice(0, half);
  const col2 = items?.slice(half, items.length);

  {
    /* 
  Note, deliberately not using an `ul` element as:
  a) value of doing so is questionable, and
  b) it may confuse people if we tell them a list has say 5 items, only for 
  them to not realise afterwards that there's _another_ list with 4/5 items!
    */
  }
  return thresholdMet ? (
    <>
      <div className="main-nav-desktop__sub-menu-list">
        {col1.map((item, i) => (
          <SubmenuItem key={`col_1_${i}`} item={item} />
        ))}
      </div>
      <div className="main-nav-desktop__sub-menu-list">
        {col2.map((item, i) => (
          <SubmenuItem
            key={`col_2_${i}`}
            item={item}
            isLast={i === col2.length - 1}
          />
        ))}
      </div>
    </>
  ) : (
    <div className="main-nav-desktop__sub-menu-list">
      {items.map((item, i) => (
        <SubmenuItem
          key={`col_1_${i}`}
          item={item}
          isLast={i === items.length - 1}
        />
      ))}
    </div>
  );
};

const DesktopMenuItem = ({
  item,
  isOpen,
  onClick,
  dropdownRef,
}: DesktopMenuItemProps): JSX.Element => {
  // Unique ID for a11y purposes (to link controls to the things they control)
  const uniqueA11yId = useId();

  return (
    <li className="main-nav-desktop__main-item">
      {item.l2_items.length > 0 || item.isSearch ? (
        <>
          <button
            className={cx('main-nav-desktop__item', {
              'main-nav-desktop__item--open': isOpen,
              'main-nav-desktop__item--current-section': item.is_current,
            })}
            onClick={onClick}
            aria-controls={`${uniqueA11yId}_desktop`}
            aria-expanded={isOpen}
          >
            <span>{item.title}</span>
            {item.isSearch ? (
              <Svg
                sprite="two-tone"
                svg="search"
                className="main-nav-desktop__search-icon"
              />
            ) : (
              <Svg
                sprite="two-tone"
                svg={isOpen ? 'chevron-up' : 'chevron-down'}
                className="main-nav-desktop__dropdown-icon"
              />
            )}
          </button>

          {isOpen && (
            <div
              className="main-nav-desktop__sub-menu"
              id={`${uniqueA11yId}_desktop`}
              ref={dropdownRef}
            >
              <div className="main-nav-desktop__sub-menu-grid grid-standard content-width">
                <div className="main-nav-desktop__sub-menu-overview">
                  <h2>{item.title}</h2>
                  {item.overview && <p>{item.overview}</p>}
                  {!item.isSearch && (
                    <a
                      href={item.link_url}
                      className="main-nav-desktop__sub-menu-goto-link sk-btn sk-btn--secondary"
                      // Overview link is always the first link in the dropdown.
                      data-is-first="true"
                    >
                      <span>Go to section overview</span>
                      <Svg sprite="two-tone" svg="chevron-right" />
                    </a>
                  )}
                </div>

                <div className="main-nav-desktop__sub-menu-main-content">
                  {!item.isSearch ? (
                    <SubmenuColumns items={item.l2_items} />
                  ) : (
                    <SearchForm
                      searchUrl={item.link_url}
                      extraClasses="main-nav-desktop__search-form"
                    />
                  )}
                </div>
              </div>
            </div>
          )}
        </>
      ) : (
        <a
          href={item.link_url}
          className={cx('main-nav-desktop__item', {
            'main-nav-desktop__item--current-section': item.is_current,
          })}
          aria-current={item.is_current ? 'page' : undefined}
        >
          <span>{item.title}</span>
        </a>
      )}
    </li>
  );
};

export default DesktopMenuItem;
