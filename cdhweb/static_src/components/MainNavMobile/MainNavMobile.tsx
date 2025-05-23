import { JSX, useState } from 'react';
import MainNavMobileItem from './MainNavMobileItem';
import {
  MainNavDataPrimarySimplified,
  MainNavDataSecondarySimplified,
} from '../../data-types';
import Svg from '../svg/svg';
import cx from 'classnames';
import SearchForm from '../SearchForm/SearchForm';

type DesktopMenuDataType = {
  primaryNavData: MainNavDataPrimarySimplified;
  secondaryNavData: MainNavDataSecondarySimplified;
  searchUrl: string;
};

const MainNavMobile = ({
  primaryNavData,
  secondaryNavData,
  searchUrl,
}: DesktopMenuDataType): JSX.Element => {
  const [menuIsOpen, setMenuIsOpen] = useState(false);
  return (
    <>
      <div
        className={cx('mobile-menu__header', {
          'mobile-menu__header--open': menuIsOpen,
        })}
      >
        <a
          href="/"
          className="mobile-menu__logo-link"
          aria-label="The Center for Digital Humanities at Princeton"
        >
          <Svg
            sprite="logo"
            svg="cdh-logo"
            className="mobile-menu__header-logo"
          />
        </a>

        <button
          type="button"
          className={cx('sk-btn sk-btn--secondary mobile-menu__header-btn', {
            'mobile-menu__header-btn--active': menuIsOpen,
          })}
          onClick={() => setMenuIsOpen(!menuIsOpen)}
          aria-expanded={menuIsOpen ? true : false}
        >
          <span>{menuIsOpen ? 'Close' : 'Menu'}</span>
          <Svg
            sprite="two-tone"
            svg={menuIsOpen ? 'x' : 'hamburger'}
            className="mobile-menu__header-btn-icon"
          />
        </button>
      </div>
      {menuIsOpen && (
        <div className="mobile-menu__nav-container">
          <div className="content-width">
            {primaryNavData.length > 0 && (
              <ul className="mobile-menu__nav-list">
                {primaryNavData.map((item, i) => (
                  <MainNavMobileItem
                    item={item}
                    key={i}
                    uniqueItemId={`mobile-nav-item_${i}`}
                  />
                ))}
              </ul>
            )}

            <div className="mobile-menu__secondary-content">
              <h2>Search</h2>
              <SearchForm searchUrl={searchUrl} />

              {secondaryNavData.items.length > 0 && (
                <ul className="mobile-menu__secondary-nav-list">
                  {secondaryNavData.items.map((item, i) => (
                    <li key={i}>
                      <a href={item.link_url}>
                        <span>{item.title}</span>
                      </a>
                    </li>
                  ))}
                </ul>
              )}

              {/* There should only be max 1 CTA. If there are any, render only the first. */}
              {secondaryNavData &&
                secondaryNavData.cta &&
                secondaryNavData.cta.length > 0 && (
                  <a
                    href={secondaryNavData.cta[0].link_url}
                    className="sk-btn sk-btn--secondary mobile-menu__cta"
                  >
                    {secondaryNavData.cta[0].title}
                  </a>
                )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default MainNavMobile;
